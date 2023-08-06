
#include <stdio.h>

int
main (void)
{
    char transa = 'N', transb = 'N';
    int lda = 2;
    int ldb = 3;
    int n = 2, m = 2, k = 3;
    float alpha = 1.0, beta = 0.0;

    float A[] = {1, 4,
		 2, 5,
		 3, 6};

    float B[] = {1, 3, 5,
	         2, 4, 6}; 
    int ldc = 2;
    float C[] = { 0.00, 0.00,
                 0.00, 0.00 };

    /* Compute C = A B */
    sgemm_(&transa, &transb, &n, &m, &k,
          &alpha, A, &lda, B, &ldb, &beta, C, &ldc);

    printf("C = {%f, %f; %f, %f}\n", C[0], C[2], C[1], C[3]);
    return 0;  
}

#if  0
library_dirs : ['']
rpath : ['']
frameworks : ['Accelerate']
linkflagsend : ['-L/usr/local/gfortran/lib/gcc/i386-apple-darwin8.10.1/4.4.0', '-L/usr/local/gfortran/lib/gcc/i386-apple-darwin8.10.1/4.4.0/../../..', '-lgfortranbegin', '-lgfortran']
include_dirs : ['/usr/local/include', '/usr/include']
#endif

