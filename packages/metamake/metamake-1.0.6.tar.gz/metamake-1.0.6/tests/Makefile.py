from metamake import task, bootstrap

bootstrap("Makefile.test")

@task
def testA():
    """runs testA"""
    print "running task: testA"
