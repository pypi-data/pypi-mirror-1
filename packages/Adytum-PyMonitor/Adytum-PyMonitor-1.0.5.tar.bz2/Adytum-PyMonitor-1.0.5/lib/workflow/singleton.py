from adytum.workflow.base import Workflow, WorkflowAware
from adytum.patterns.singleton import Singleton

class SingletonWorkflowAware(Singleton, WorkflowAware):
    '''
    # setup workflow 1
    >>> swf1 = SingletonWorkflow()
    >>> swf1.addState('Normal')
    >>> swf1.addState('Warn')
    >>> swf1.addTrans('Normaling', 'Warn', 'Normal')
    >>> swf1.addTrans('Warning', 'Normal', 'Warn')
    >>> swf1.setInitState('Normal')

    # setup workflow 2
    >>> swf2 = SingletonWorkflow()
    >>> swf2.addState('Normal')
    >>> swf2.addState('Warn')
    >>> swf2.addTrans('Normaling', 'Warn', 'Normal')
    >>> swf2.addTrans('Warning', 'Normal', 'Warn')
    >>> swf2.setInitState('Normal')

    >>> assert(id(swf1) == id(swf2)), "We've got a problem, Jim..."

    # get some instantiations running
    >>> class AppState(SingletonWorkflowAware):
    ...   def __init__(self, workflow=None):
    ...     self.enterWorkflow(workflow, None, 'Just Created')
    >>> as1 = AppState(swf1)
    >>> as2 = AppState(swf2)
    >>> as1.doTrans('Warning')

    >>> assert(as1.workflow_state is as2.workflow_state), "Oops, these should be the same"
    ''' 

class SingletonWorkflow(Singleton, Workflow):
    pass

def _test():
    import doctest, singleton
    doctest.testmod(singleton)

if __name__ == '__main__':
    _test()
