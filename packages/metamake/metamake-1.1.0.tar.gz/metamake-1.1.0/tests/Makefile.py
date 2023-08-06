from metamake import task, bootstrap, shell

bootstrap("Makefile.test")

@task
def testA():
    """runs testA"""
    print "running task: testA"

@task
def task_that_will_fail():
    shell("nonexistent_binary_on_your_system")
    print "running task: task_that_will_fail"