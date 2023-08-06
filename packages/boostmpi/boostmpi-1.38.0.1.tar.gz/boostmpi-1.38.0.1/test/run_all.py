from glob import glob
import boostmpi

tests = boostmpi.broadcast(value=glob("*test.py"), root=0)

broken_tests = ["ring_test.py", "skeleton_content_test.py"]

for testfile in tests:
    if testfile in broken_tests:
        continue

    if boostmpi.rank == 0:
        print "----------------------------------------------------"
        print testfile
        print "----------------------------------------------------"

    boostmpi.world.barrier()
    mod = __import__(testfile[:-3])
    mod.run_test()
    boostmpi.world.barrier()
