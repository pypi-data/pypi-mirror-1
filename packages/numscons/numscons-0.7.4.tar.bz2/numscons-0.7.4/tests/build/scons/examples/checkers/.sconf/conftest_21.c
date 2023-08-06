
#define our_fancy_func sgesv_

extern int our_fancy_func(int *n, int *nrhs, float a[], int *lda, int ipiv[], 
                  float b[], int *ldb, int *info);

int compare(float A[], float B[], int sz)
{
        int i;

        for(i = 0; i < sz; ++i) {
                if ( (A[i] - B[i] > 0.01) || (A[i] - B[i] < -0.01)) {
                        return -1;
                }
        }
        return 0;
}

int main(void)
{
    int n = 2;
    int nrhs = 2;
    int lda = 2;
    float A[] = { 1, 3, 2, 4};

    int ldb = 2;
    float B[] = { 1, 0, 0, 1};
    float X[] = { -2, 1.5, 1, -0.5};

    int ipov[] = {0, 0};
    int info;

    /* Compute X in A * X = B */
    our_fancy_func(&n, &nrhs, A, &lda, ipov, B, &ldb, &info);

    return compare(B, X, 4);
}

#if  0
library_dirs : ['']
rpath : ['']
frameworks : ['Accelerate']
linkflagsend : ['-L/usr/local/gfortran/lib/gcc/i386-apple-darwin8.10.1/4.4.0', '-L/usr/local/gfortran/lib/gcc/i386-apple-darwin8.10.1/4.4.0/../../..', '-lgfortranbegin', '-lgfortran']
include_dirs : ['/usr/local/include', '/usr/include']
#endif

