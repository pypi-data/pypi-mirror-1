from mpi4py import MPI

errors = ['SUCCESS',
          'ERR_ARG',
          'ERR_BUFFER',
          'ERR_COMM',
          'ERR_COUNT',
          'ERR_DIMS',
          'ERR_GROUP',
          'ERR_INTERN',
          'ERR_IN_STATUS',
          #'ERR_LASTCODE',
          'ERR_OP',
          'ERR_OTHER',
          'ERR_PENDING',
          'ERR_RANK',
          'ERR_REQUEST',
          'ERR_ROOT',
          'ERR_TAG',
          'ERR_TOPOLOGY',
          'ERR_TRUNCATE',
          'ERR_TYPE',
          'ERR_UNKNOWN']

print '='*70
print 'MPI Errors'.center(70)
print '='*70

format = '%-13s  %4s  %-48s'
print format % ('Name'.center(13), 'Code', 'String'.center(48))
print format % ('='*13,'='*4,'='*49)
for errname in errors:
    ierr = getattr(MPI,errname)
    print format % (errname,ierr,MPI.Get_error_string(ierr))
print format % ('='*13,'='*4,'='*49)
