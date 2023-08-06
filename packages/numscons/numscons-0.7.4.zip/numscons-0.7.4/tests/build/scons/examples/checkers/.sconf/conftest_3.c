
#undef cblas_sgemm
#ifdef __cplusplus
extern "C"
#endif
char cblas_sgemm();

int main()
{
return cblas_sgemm();
return 0;
}

#if 0
library_dirs : ['']
rpath : ['']
frameworks : ['Accelerate']
include_dirs : ['/usr/local/include', '/usr/include']
#endif

