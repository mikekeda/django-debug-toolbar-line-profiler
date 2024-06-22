import cProfile
import inspect
from io import StringIO
from pstats import Stats

from debug_toolbar import settings as dt_settings
from debug_toolbar.panels import Panel
from debug_toolbar.panels.profiling import FunctionCall as DjDTFunctionCall
from django.urls import resolve
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View
from line_profiler import LineProfiler, show_func

from . import signals


class FunctionCall(DjDTFunctionCall):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.has_subfuncs = False
        self._line_stats_text = None

    def subfuncs(self):
        h, s, _ = self.hsv
        count = len(self.statobj.all_callees[self.func])
        for i, (func, stats) in enumerate(self.statobj.all_callees[self.func].items(), 1):
            h1 = h + (i / count) / (self.depth + 1)
            s1 = 0 if stats[3] == 0 or self.stats[3] == 0 else s * (stats[3] / self.stats[3])

            yield FunctionCall(
                self.statobj,
                func,
                self.depth + 1,
                stats=stats,
                id=f'{self.id}_{i}',
                parent_ids=[*self.parent_ids, self.id],
                hsv=(h1, s1, 1),
            )

    def line_stats_text(self):
        if self._line_stats_text is None:
            lstats = self.statobj.line_stats
            if self.func in lstats.timings:
                out = StringIO()
                fn, lineno, name = self.func
                try:
                    show_func(fn, lineno, name, lstats.timings[self.func], lstats.unit, stream=out)
                    self._line_stats_text = out.getvalue()
                except ZeroDivisionError:
                    self._line_stats_text = 'There was a ZeroDivisionError, total_time was probably zero'
            else:
                self._line_stats_text = False
        return self._line_stats_text


class ProfilingPanel(Panel):
    """Panel that displays profiling information."""

    capture_project_code = dt_settings.get_config()['PROFILER_CAPTURE_PROJECT_CODE']

    @property
    def title(self) -> str:
        return _('Profiling')

    @property
    def template(self) -> str:
        return 'debug_toolbar_line_profiler/panels/profiling.html'

    def _unwrap_closure_and_profile(self, func) -> None:
        if not hasattr(func, '__code__') or func in self.added:
            return

        self.added.add(func)

        self.line_profiler.add_function(func)
        for subfunc in getattr(func, 'profile_additional', []):
            self._unwrap_closure_and_profile(subfunc)

        if func_closure := func.__closure__:
            for cell in func_closure:
                target = cell.cell_contents
                if hasattr(target, '__code__'):
                    self._unwrap_closure_and_profile(target)
                if inspect.isclass(target) and View in inspect.getmro(target):
                    for name, value in inspect.getmembers(target):
                        if not name.startswith('__') and (inspect.ismethod(value) or inspect.isfunction(value)):
                            self._unwrap_closure_and_profile(value)

    def process_request(self, request):
        self.view_func, view_args, view_kwargs = resolve(request.path)
        self.profiler = cProfile.Profile()
        self.line_profiler = LineProfiler()
        self.added = set()
        self._unwrap_closure_and_profile(self.view_func)
        signals.profiler_setup.send(
            sender=self,
            profiler=self.line_profiler,
            view_func=self.view_func,
            view_args=view_args,
            view_kwargs=view_kwargs,
        )
        self.line_profiler.enable_by_count()
        out = self.profiler.runcall(super().process_request, request)
        self.line_profiler.disable_by_count()
        return out

    def add_node(self, func_list: list, func: FunctionCall, max_depth: int, cum_time: float):
        """add_node does a depth first traversal of the call graph, appending a FunctionCall object to func_list, so
        that the Django template only has to do a single for loop over func_list that can render a tree structure.

        Parameters
        ----------
            func_list is an array that will have a FunctionCall for each call added to it
            func is a FunctionCall object that will have all its callees added
            max_depth is the maximum depth we should recurse
            cum_time is the minimum cum_time a function should have to be included in the output

        """
        func_list.append(func)
        func.has_subfuncs = False
        # this function somewhat dangerously relies on FunctionCall to set its subfuncs' depth argument correctly
        if func.depth >= max_depth:
            return

        subs = sorted(func.subfuncs(), key=FunctionCall.cumtime, reverse=True)
        for subfunc in subs:
            # a sub function is important if it takes a long time or it has line_stats
            is_project_code = bool(self.capture_project_code and subfunc.is_project_func())
            if (
                subfunc.cumtime() >= cum_time
                or (is_project_code and subfunc.cumtime() > 0)
                or (hasattr(self.stats, 'line_stats') and subfunc.func in self.stats.line_stats.timings)
            ):
                func.has_subfuncs = True
                self.add_node(
                    func_list=func_list,
                    func=subfunc,
                    max_depth=max_depth,
                    cum_time=subfunc.cumtime() / dt_settings.get_config()['PROFILER_THRESHOLD_RATIO'] / 2,
                )

    def generate_stats(self, request, response):
        if not hasattr(self, 'profiler'):
            return
        # Could be delayed until the panel content is requested (perf. optim.)
        self.profiler.create_stats()
        self.stats = Stats(self.profiler)
        self.stats.line_stats = self.line_profiler.get_stats()
        self.stats.calc_callees()

        func_list = []
        if root_func := cProfile.label(self.view_func.__code__):
            root_node = FunctionCall(statobj=self.stats, func=root_func, depth=0)
            self.add_node(
                func_list=func_list,
                func=root_node,
                max_depth=dt_settings.get_config()['PROFILER_MAX_DEPTH'],
                cum_time=root_node.cumtime() / dt_settings.get_config()['PROFILER_THRESHOLD_RATIO'],
            )
        # else:
        # what should we do if we didn't detect a root function? It's not
        # clear what causes this, but there are real world examples of it (see
        # https://github.com/dmclain/django-debug-toolbar-line-profiler/issues/11)

        self.record_stats({'func_list': func_list})
