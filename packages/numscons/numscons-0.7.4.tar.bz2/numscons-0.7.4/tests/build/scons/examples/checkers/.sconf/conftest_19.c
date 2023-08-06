
enum CBLAS_ORDER {CblasRowMajor=101, CblasColMajor=102};
enum CBLAS_TRANSPOSE {CblasNoTrans=111, CblasTrans=112, CblasConjTrans=113};

void cblas_sgemm(const enum CBLAS_ORDER Order, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_TRANSPOSE TransB, const int M, const int N,
                 const int K, const float alpha, const float *A,
                 const int lda, const float *B, const int ldb,
                 const float beta, float *C, const int ldc);
int
main (void)
{
    int lda = 3;
    float A[] = {1, 2, 3,
                 4, 5, 6};

    int ldb = 2;
    float B[] = {1, 2, 
	         3, 4,
		 5, 6};

    int ldc = 2;
    float C[] = { 0.00, 0.00,
                 0.00, 0.00 };

    /* Compute C = A B */
    cblas_sgemm (CblasRowMajor, 
                CblasNoTrans, CblasNoTrans, 2, 2, 3,
                1.0, A, lda, B, ldb, 0.0, C, ldc);

    return 0;  
}

#if  0
rpath : ['']
frameworks : ['Accelerate']
library_dirs : ['']
include_dirs : ['/usr/local/include', '/usr/include']
#endif

