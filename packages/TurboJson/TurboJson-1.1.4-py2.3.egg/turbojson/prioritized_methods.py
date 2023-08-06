""""prioritized_methods

This is an extension to RuleDispatch to prioritize methods in order
to avoid AmbiguousMethods situations.

Copied from ToscaWidgets, thanks to Alberto Valverde Gonzalez.

"""

import sys

from dispatch import strategy, functions
from dispatch.interfaces import ICriterion, IDispatchPredicate, AmbiguousMethod
from peak.util.decorators import decorate_assignment, frameinfo, decorate_class

__all__ = ['PriorityDisambiguated', 'default_rule', 'generic']

try:
    set
except NameError: # Python 2.3
    from sets import Set as set

default_rule = strategy.default


def _prioritized_safe_methods(grouped_cases):
    """Yield methods in 'grouped_cases', strict version.

    Yield all methods in 'grouped_cases' including those in groups with
    more than one case (AmbiguousMethods) in the priority specified by the
    priority defined when decorating the method.

    Priorities must be distinct within a group of ambiguous methods or else
    an AmbiguousMethod will be raised.

    """
    for group in grouped_cases:
        if len(group) > len(set([meth._prio for sig, meth in group])):
            yield AmbiguousMethod(group)
            break
        elif len(group) > 1:
            methods = [(-meth._prio, meth) for sig, meth in group]
            methods.sort()
            for prio, meth in methods:
                yield meth
        else:
            yield group[0][1]


def _prioritized_all_methods(grouped_cases):
    """Yield methods in 'grouped_cases', loose version.

    Yield all methods in 'grouped_cases' including those in groups with
    more than one case (AmbiguousMethods) in the priority specified by the
    priority defined when decorating the method.

    """
    for group in grouped_cases:
        methods = [(-meth._prio, meth) for sig, meth in group]
        methods.sort()
        for prio, meth in methods:
            yield meth


class PriorityDisambiguated(functions.GenericFunction):
    """GenericFunction with additional priority parameter.

    Remimplementation of dispatch.functions.GenericFunction allowing the case
    decorators to specify a priority for ordering and disambiguation purposes.

    """

    def combine(self, cases):
        """Combine method using priority-ordering generators.

        Same as GenericFunction.combine but replaces strategy.safe_methods
        and strategy.all_methods with priority-ordering generators.

        """
        strict = [strategy.ordered_signatures, _prioritized_safe_methods]
        loose  = [strategy.ordered_signatures, _prioritized_all_methods]
        cases = strategy.separate_qualifiers(cases,
            around=strict, before=loose, primary=strict, after=loose)
        primary = strategy.method_chain(cases.get('primary', []))
        if cases.get('after') or cases.get('before'):
            befores = strategy.method_list(cases.get('before', []))
            afters = strategy.method_list(list(cases.get('after', []))[::-1])
            def chain(*args, **kw):
                for tmp in befores(*args, **kw):
                    pass # toss return values
                result = primary(*args, **kw)
                for tmp in afters(*args, **kw):
                    pass # toss return values
                return result
        else:
            chain = primary
        if cases.get('around'):
            chain = strategy.method_chain(list(cases['around']) + [chain])
        return chain

    def around(self, cond, prio=0):
        """Add function as an 'around' method with 'cond' as a guard.

        If 'cond' is parseable, it will be parsed using the caller's frame
        locals and globals.

        """
        return self._decorate(cond, 'around', prio=prio)

    def before(self, cond, prio=0):
        """Add function as a 'before' method with 'cond' as a guard.

        If 'cond' is parseable, it will be parsed using the caller's frame
        locals and globals.

        """
        return self._decorate(cond, 'before', prio=prio)


    def after(self, cond, prio=0):
        """Add function as an 'after' method with 'cond' as a guard.

        If 'cond' is parseable, it will be parsed using the caller's frame
        locals and globals.

        """
        return self._decorate(cond, 'after', prio=prio)


    def when(self, cond, prio=0):
        """Add following function to this generic one, with 'cond' as a guard.

        If 'cond' is parseable, it will be parsed using the caller's frame
        locals and globals.

        """
        return self._decorate(cond, 'primary', prio=prio)

    def _decorate(self, cond, qualifier=None, frame=None, depth=2, prio=0):
        """Decorate method with priority parameter.

        Analogous to AbstractGeneric._decorate but accepts a priority
        parameter to attach as an attribute to the decorated method to aid
        in disambiguation/ordering.

        """
        frame = frame or sys._getframe(depth)
        rule = cond
        cond = self.parseRule(cond, frame=frame) or cond

        def registerMethod(frm, name, value, old_locals):
            kind, module, locals_, globals_ = frameinfo(frm)
            if qualifier is None:
                func = value
            else:
                func = qualifier, value
            if kind == 'class':
                # 'when()' in class body; defer adding the method
                def registerClassSpecificMethod(cls):
                    req = strategy.Signature(
                        [(strategy.Argument(0), ICriterion(cls))])
                    self.addMethod(req & cond, func, prio=prio)
                    return cls
                decorate_class(registerClassSpecificMethod, frame=frm)
            else:
                self.addMethod(cond, func, prio=prio)
            if old_locals.get(name) in (self, self.delegate):
                return self.delegate
            return value

        return decorate_assignment(registerMethod, frame=frame)

    def addMethod(self, predicate, function, qualifier=None, prio=0):
        if isinstance(function, tuple):
            function[1]._prio = prio
        else:
            function._prio = prio
        if qualifier is not None:
            function = qualifier, function
        for signature in IDispatchPredicate(predicate):
            self[signature] = function
