extern "C" {
#include "Python.h" // must be included first
#include "structmember.h" // python struct
#include "png.h" // png
}

#include <iostream>
// #include <hash_map>
#include <map>
using namespace std;

#define CLOSURE(rtype, fname, args, body) class fname##_ { public: static rtype fname args body; }; rtype (*fname) args = &fname##_::fname;
#define PYLENGTH(aa) ((int) PyObject_Length(aa))
#define MAX(aa, bb) ((aa) > (bb) ? (aa) : (bb))
#define MIN(aa, bb) ((aa) < (bb) ? (aa) : (bb))
#define SWAP(aa, bb, cc) cc = aa; aa = bb; bb = cc;
inline void divabcd(int aa, int bb, int *cc, int *dd) { *cc = aa / bb; *dd = aa % bb; }
typedef ssize_t ssz; typedef unsigned char uch; typedef unsigned int uint; typedef long long i64;  int ERROR = -1;
#define PYVSNPRINTF(ss, ll, fmt) char ss[ll]; va_list args; va_start(args, fmt); vsnprintf(ss, ll, fmt, args); va_end(args);
void pyprint(const char *fmt, ...) { PYVSNPRINTF(ss, 1024, fmt); PyFile_WriteString(ss, PySys_GetObject("stdout")); }
PyObject *pyerr(PyObject *err, const char *fmt, ...) { PYVSNPRINTF(ss, 1024, fmt); PyErr_SetString(err, ss); return err; }







namespace IMG2TXT {
  //// itp algorithm
  const i64 FBMP0[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x100104104100LL,0xa28aLL,0x1457caf94500LL,0x43d450c1c5784LL,0x46a50c295880LL,0x799b6638a100LL,0x4104LL,0x30204104104230LL,0x3108208208103LL,0xa19b100LL,0x1047c4100000LL,0x10830c000000000LL,0x1e000000LL,0x30c000000000LL,0x108210c210420LL,0x391451451380LL,0x7c4104105180LL,0x782108410380LL,0x39040c410780LL,0x2087c928c200LL,0x39040e082780LL,0x3914cd042700LL,0x82104210780LL,0x39144e251380LL,0x1c841e451380LL,0x30c00c300000LL,0x10830c00c300000LL,0x40c0cc400000LL,0x3f03f000000LL,0x46606040000LL,0x100108412780LL,0x781f55751780LL,0x85279228c300LL,0x3d144f4513c0LL,0x702041042700LL,0x3d14514513c0LL,0x78208e082780LL,0x8208e082780LL,0x712459042700LL,0x45145f451440LL,0x7c41041047c0LL,0x188208208380LL,0x449143149440LL,0x782082082080LL,0x4555576db440LL,0x4596555d3440LL,0x391451451380LL,0x4104f4513c0LL,0x30391451451380LL,0x4491472491c0LL,0x39040c082700LL,0x1041041047c0LL,0x391451451440LL,0x10c292491840LL,0x28a3d5555440LL,0x852308312840LL,0x10410428a440LL,0x7c10842107c0LL,0x1c10410410411cLL,0x20410204102081LL,0xe20820820820eLL,0x1128a284100LL,0x3f000000000000LL,0x204LL,0xf92710380000LL,0x3d1453341041LL,0x781041780000LL,0x599451790410LL,0x7817d1380000LL,0x104104784118LL,0x390599451780000LL,0x451453741041LL,0x208208380008LL,0x1c8208208380008LL,0x48a18a482082LL,0x104104104107LL,0x5555557c0000LL,0x451453740000LL,0x391451380000LL,0x413d1453340000LL,0x410599451780000LL,0x82096680000LL,0x390302700000LL,0x604104784100LL,0x5d9451440000LL,0x10a28a440000LL,0x492b6d940000LL,0x44a10a440000LL,0xc430c492840000LL,0x7c21087c0000LL,0x1c10410210411cLL,0x4104104104104LL,0xe20821020820eLL,0xe67000000LL,0x0LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0xfffffffffffffffLL,0xfffeffefbefbeffLL,0xfffffffffff5d75LL,0xfffeba83506baffLL,0xffbc2baf3e3a87bLL,0xfffb95af3d6a77fLL,0xfff866499c75effLL,0xfffffffffffbefbLL,0xfcfdfbefbefbdcfLL,0xffcef7df7df7efcLL,0xffffffff5e64effLL,0xfffefb83befffffLL,0xef7cf3fffffffffLL,0xfffffffe1ffffffLL,0xfffcf3fffffffffLL,0xffef7def3defbdfLL,0xfffc6ebaebaec7fLL,0xfff83befbefae7fLL,0xfff87def7befc7fLL,0xfffc6fbf3bef87fLL,0xfffdf7836d73dffLL,0xfffc6fbf1f7d87fLL,0xfffc6eb32fbd8ffLL,0xffff7defbdef87fLL,0xfffc6ebb1daec7fLL,0xfffe37be1baec7fLL,0xfffcf3ff3cfffffLL,0xef7cf3ff3cfffffLL,0xfffbf3f33bfffffLL,0xffffc0fc0ffffffLL,0xffffb99f9fbffffLL,0xfffeffef7bed87fLL,0xfff87e0aa8ae87fLL,0xfff7ad86dd73cffLL,0xfffc2ebb0baec3fLL,0xfff8fdfbefbd8ffLL,0xfffc2ebaebaec3fLL,0xfff87df71f7d87fLL,0xffff7df71f7d87fLL,0xfff8edba6fbd8ffLL,0xfffbaeba0baebbfLL,0xfff83befbefb83fLL,0xfffe77df7df7c7fLL,0xfffbb6ebceb6bbfLL,0xfff87df7df7df7fLL,0xfffbaaaa8924bbfLL,0xfffba69aaa2cbbfLL,0xfffc6ebaebaec7fLL,0xffffbefb0baec3fLL,0xfcfc6ebaebaec7fLL,0xfffbb6eb8db6e3fLL,0xfffc6fbf3f7d8ffLL,0xfffefbefbefb83fLL,0xfffc6ebaebaebbfLL,0xfffef3d6db6e7bfLL,0xfffd75c2aaaabbfLL,0xfff7adcf7ced7bfLL,0xfffefbefbd75bbfLL,0xfff83ef7bdef83fLL,0xfe3efbefbefbee3LL,0xfdfbefdfbefdf7eLL,0xff1df7df7df7df1LL,0xffffeed75d7beffLL,0xfc0ffffffffffffLL,0xffffffffffffdfbLL,0xfff06d8efc7ffffLL,0xfffc2ebaccbefbeLL,0xfff87efbe87ffffLL,0xfffa66bae86fbefLL,0xfff87e82ec7ffffLL,0xfffefbefb87bee7LL,0xc6fa66bae87ffffLL,0xfffbaebac8befbeLL,0xfffdf7df7c7fff7LL,0xe37df7df7c7fff7LL,0xfffb75e75b7df7dLL,0xfffefbefbefbef8LL,0xfffaaaaaa83ffffLL,0xfffbaebac8bffffLL,0xfffc6ebaec7ffffLL,0xfbec2ebaccbffffLL,0xbefa66bae87ffffLL,0xffff7df6997ffffLL,0xfffc6fcfd8fffffLL,0xfff9fbefb87beffLL,0xfffa26baebbffffLL,0xfffef5d75bbffffLL,0xfffb6d4926bffffLL,0xfffbb5ef5bbffffLL,0xf3bcf3b6d7bffffLL,0xfff83def783ffffLL,0xfe3efbefdefbee3LL,0xffbefbefbefbefbLL,0xff1df7defdf7df1LL,0xffffff198ffffffLL,0xfffffffffffffffLL};
  const i64 FBMP1[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x4004104104LL,0x28aLL,0x515f2be514LL,0x10f51430715eLL,0x11a9430a562LL,0x1e66d98e284LL,0x104LL,0xc08104104108LL,0xc4208208204LL,0x2866c4LL,0x411f104000LL,0x420c300000000LL,0x780000LL,0xc300000000LL,0x42084308410LL,0xe45145144eLL,0x1f104104146LL,0x1e08421040eLL,0xe41031041eLL,0x821f24a308LL,0xe41038209eLL,0xe45334109cLL,0x208410841eLL,0xe45138944eLL,0x721079144eLL,0xc30030c000LL,0x420c30030c000LL,0x10303310000LL,0xfc0fc0000LL,0x1198181000LL,0x400421049eLL,0x1e07d55d45eLL,0x2149e48a30cLL,0xf4513d144fLL,0x1c08104109cLL,0xf45145144fLL,0x1e08238209eLL,0x208238209eLL,0x1c49164109cLL,0x114517d1451LL,0x1f10410411fLL,0x620820820eLL,0x112450c5251LL,0x1e082082082LL,0x115555db6d1LL,0x116595574d1LL,0xe45145144eLL,0x10413d144fLL,0xc0e45145144eLL,0x112451c9247LL,0xe41030209cLL,0x410410411fLL,0xe451451451LL,0x430a492461LL,0xa28f555551LL,0x2148c20c4a1LL,0x410410a291LL,0x1f04210841fLL,0x704104104104LL,0x810408104082LL,0x388208208208LL,0x44a28a104LL,0xfc0000000000LL,0x8LL,0x3e49c40e000LL,0xf4514cd041LL,0x1e04105e000LL,0x1665145e410LL,0x1e05f44e000LL,0x410411e104LL,0xe41665145e000LL,0x114514dd041LL,0x820820e000LL,0x720820820e000LL,0x12286292082LL,0x4104104104LL,0x1555555f000LL,0x114514dd000LL,0xe45144e000LL,0x104f4514cd000LL,0x1041665145e000LL,0x208259a000LL,0xe40c09c000LL,0x1810411e104LL,0x17651451000LL,0x428a291000LL,0x124adb65000LL,0x11284291000LL,0x310c3124a1000LL,0x1f08421f000LL,0x704104084104LL,0x104104104104LL,0x388208408208LL,0x399c0000LL,0x0LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x3fffffffffffffLL,0x3fffbffbefbefbLL,0x3ffffffffffd75LL,0x3fffaea0d41aebLL,0x3fef0aebcf8ea1LL,0x3ffee56bcf5a9dLL,0x3ffe1992671d7bLL,0x3ffffffffffefbLL,0x3f3f7efbefbef7LL,0x3ff3bdf7df7dfbLL,0x3fffffffd7993bLL,0x3fffbee0efbfffLL,0x3bdf3cffffffffLL,0x3fffffff87ffffLL,0x3fff3cffffffffLL,0x3ffbdf7bcf7befLL,0x3fff1baebaebb1LL,0x3ffe0efbefbeb9LL,0x3ffe1f7bdefbf1LL,0x3fff1befcefbe1LL,0x3fff7de0db5cf7LL,0x3fff1befc7df61LL,0x3fff1baccbef63LL,0x3fffdf7bef7be1LL,0x3fff1baec76bb1LL,0x3fff8def86ebb1LL,0x3fff3cffcf3fffLL,0x3bdf3cffcf3fffLL,0x3ffefcfcceffffLL,0x3ffff03f03ffffLL,0x3fffee67e7efffLL,0x3fffbffbdefb61LL,0x3ffe1f82aa2ba1LL,0x3ffdeb61b75cf3LL,0x3fff0baec2ebb0LL,0x3ffe3f7efbef63LL,0x3fff0baebaebb0LL,0x3ffe1f7dc7df61LL,0x3fffdf7dc7df61LL,0x3ffe3b6e9bef63LL,0x3ffeebae82ebaeLL,0x3ffe0efbefbee0LL,0x3fff9df7df7df1LL,0x3ffeedbaf3adaeLL,0x3ffe1f7df7df7dLL,0x3ffeeaaaa2492eLL,0x3ffee9a6aa8b2eLL,0x3fff1baebaebb1LL,0x3fffefbec2ebb0LL,0x3f3f1baebaebb1LL,0x3ffeedbae36db8LL,0x3fff1befcfdf63LL,0x3fffbefbefbee0LL,0x3fff1baebaebaeLL,0x3fffbcf5b6db9eLL,0x3fff5d70aaaaaeLL,0x3ffdeb73df3b5eLL,0x3fffbefbef5d6eLL,0x3ffe0fbdef7be0LL,0x3f8fbefbefbefbLL,0x3f7efbf7efbf7dLL,0x3fc77df7df7df7LL,0x3ffffbb5d75efbLL,0x3f03ffffffffffLL,0x3ffffffffffff7LL,0x3ffc1b63bf1fffLL,0x3fff0baeb32fbeLL,0x3ffe1fbefa1fffLL,0x3ffe99aeba1befLL,0x3ffe1fa0bb1fffLL,0x3fffbefbee1efbLL,0x31be99aeba1fffLL,0x3ffeebaeb22fbeLL,0x3fff7df7df1fffLL,0x38df7df7df1fffLL,0x3ffedd79d6df7dLL,0x3fffbefbefbefbLL,0x3ffeaaaaaa0fffLL,0x3ffeebaeb22fffLL,0x3fff1baebb1fffLL,0x3efb0baeb32fffLL,0x2fbe99aeba1fffLL,0x3fffdf7da65fffLL,0x3fff1bf3f63fffLL,0x3ffe7efbee1efbLL,0x3ffe89aebaefffLL,0x3fffbd75d6efffLL,0x3ffedb5249afffLL,0x3ffeed7bd6efffLL,0x3cef3cedb5efffLL,0x3ffe0f7bde0fffLL,0x3f8fbefbf7befbLL,0x3fefbefbefbefbLL,0x3fc77df7bf7df7LL,0x3fffffc663ffffLL,0x3fffffffffffffLL};
  const i64 FBMP2[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x4004104104000LL,0x28a280LL,0x515f2be514000LL,0x10f51430715e100LL,0x11a9430a562000LL,0x1e66d98e284000LL,0x104100LL,0xc08104104108c00LL,0xc42082082040c0LL,0x2866c4000LL,0x411f104000000LL,0x20c300000000000LL,0x780000000LL,0xc300000000000LL,0x42084308410800LL,0xe45145144e000LL,0x1f104104146000LL,0x1e08421040e000LL,0xe41031041e000LL,0x821f24a308000LL,0xe41038209e000LL,0xe45334109c000LL,0x208410841e000LL,0xe45138944e000LL,0x721079144e000LL,0xc30030c000000LL,0x20c30030c000000LL,0x10303310000000LL,0xfc0fc0000000LL,0x1198181000000LL,0x400421049e000LL,0x1e07d55d45e000LL,0x2149e48a30c000LL,0xf4513d144f000LL,0x1c08104109c000LL,0xf45145144f000LL,0x1e08238209e000LL,0x208238209e000LL,0x1c49164109c000LL,0x114517d1451000LL,0x1f10410411f000LL,0x620820820e000LL,0x112450c5251000LL,0x1e082082082000LL,0x115555db6d1000LL,0x116595574d1000LL,0xe45145144e000LL,0x10413d144f000LL,0xc0e45145144e000LL,0x112451c9247000LL,0xe41030209c000LL,0x410410411f000LL,0xe451451451000LL,0x430a492461000LL,0xa28f555551000LL,0x2148c20c4a1000LL,0x410410a291000LL,0x1f04210841f000LL,0x704104104104700LL,0x810408104082040LL,0x388208208208380LL,0x44a28a104000LL,0xfc0000000000000LL,0x8100LL,0x3e49c40e000000LL,0xf4514cd041040LL,0x1e04105e000000LL,0x1665145e410400LL,0x1e05f44e000000LL,0x410411e104600LL,0x41665145e000000LL,0x114514dd041040LL,0x820820e000200LL,0x20820820e000200LL,0x12286292082080LL,0x41041041041c0LL,0x1555555f000000LL,0x114514dd000000LL,0xe45144e000000LL,0x4f4514cd000000LL,0x41665145e000000LL,0x208259a000000LL,0xe40c09c000000LL,0x1810411e104000LL,0x17651451000000LL,0x428a291000000LL,0x124adb65000000LL,0x11284291000000LL,0x10c3124a1000000LL,0x1f08421f000000LL,0x704104084104700LL,0x104104104104100LL,0x388208408208380LL,0x399c0000000LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0xfffffffffffffc0LL,0xffbffbefbefbfc0LL,0xfffffffffd75d40LL,0xffaea0d41aebfc0LL,0xef0aebcf8ea1ec0LL,0xfee56bcf5a9dfc0LL,0xfe1992671d7bfc0LL,0xfffffffffefbec0LL,0x3f7efbefbef73c0LL,0xf3bdf7df7dfbf00LL,0xffffffd7993bfc0LL,0xffbee0efbffffc0LL,0xdf3cfffffffffc0LL,0xffffff87fffffc0LL,0xff3cfffffffffc0LL,0xfbdf7bcf7bef7c0LL,0xff1baebaebb1fc0LL,0xfe0efbefbeb9fc0LL,0xfe1f7bdefbf1fc0LL,0xff1befcefbe1fc0LL,0xff7de0db5cf7fc0LL,0xff1befc7df61fc0LL,0xff1baccbef63fc0LL,0xffdf7bef7be1fc0LL,0xff1baec76bb1fc0LL,0xff8def86ebb1fc0LL,0xff3cffcf3ffffc0LL,0xdf3cffcf3ffffc0LL,0xfefcfccefffffc0LL,0xfff03f03fffffc0LL,0xffee67e7effffc0LL,0xffbffbdefb61fc0LL,0xfe1f82aa2ba1fc0LL,0xfdeb61b75cf3fc0LL,0xff0baec2ebb0fc0LL,0xfe3f7efbef63fc0LL,0xff0baebaebb0fc0LL,0xfe1f7dc7df61fc0LL,0xffdf7dc7df61fc0LL,0xfe3b6e9bef63fc0LL,0xfeebae82ebaefc0LL,0xfe0efbefbee0fc0LL,0xff9df7df7df1fc0LL,0xfeedbaf3adaefc0LL,0xfe1f7df7df7dfc0LL,0xfeeaaaa2492efc0LL,0xfee9a6aa8b2efc0LL,0xff1baebaebb1fc0LL,0xffefbec2ebb0fc0LL,0x3f1baebaebb1fc0LL,0xfeedbae36db8fc0LL,0xff1befcfdf63fc0LL,0xffbefbefbee0fc0LL,0xff1baebaebaefc0LL,0xffbcf5b6db9efc0LL,0xff5d70aaaaaefc0LL,0xfdeb73df3b5efc0LL,0xffbefbef5d6efc0LL,0xfe0fbdef7be0fc0LL,0x8fbefbefbefb8c0LL,0x7efbf7efbf7df80LL,0xc77df7df7df7c40LL,0xfffbb5d75efbfc0LL,0x3fffffffffffc0LL,0xfffffffffff7ec0LL,0xfc1b63bf1ffffc0LL,0xff0baeb32fbef80LL,0xfe1fbefa1ffffc0LL,0xfe99aeba1befbc0LL,0xfe1fa0bb1ffffc0LL,0xffbefbee1efb9c0LL,0xbe99aeba1ffffc0LL,0xfeebaeb22fbef80LL,0xff7df7df1fffdc0LL,0xdf7df7df1fffdc0LL,0xfedd79d6df7df40LL,0xffbefbefbefbe00LL,0xfeaaaaaa0ffffc0LL,0xfeebaeb22ffffc0LL,0xff1baebb1ffffc0LL,0xfb0baeb32ffffc0LL,0xbe99aeba1ffffc0LL,0xffdf7da65ffffc0LL,0xff1bf3f63ffffc0LL,0xfe7efbee1efbfc0LL,0xfe89aebaeffffc0LL,0xffbd75d6effffc0LL,0xfedb5249affffc0LL,0xfeed7bd6effffc0LL,0xef3cedb5effffc0LL,0xfe0f7bde0ffffc0LL,0x8fbefbf7befb8c0LL,0xefbefbefbefbec0LL,0xc77df7bf7df7c40LL,0xffffc663fffffc0LL,0xfffffffffffffc0LL};
  const i64 FBMP3[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x80082082080LL,0x5145LL,0x823c57ca280LL,0x21ca2860c23c2LL,0x21528614a440LL,0x3cc5931c5080LL,0x2082LL,0x18102082082118LL,0x1084104104081LL,0x50cd080LL,0x823c2080000LL,0x84186000000000LL,0xf000000LL,0x186000000000LL,0x41086108210LL,0x1c82082081c0LL,0x3c20820820c0LL,0x3c10842081c0LL,0x1c82062083c0LL,0x1043c4146100LL,0x1c82070413c0LL,0x1c8246001380LL,0x410821083c0LL,0x1c82071081c0LL,0xc420f2081c0LL,0x186006180000LL,0x84186006180000LL,0x206046200000LL,0x1f01f000000LL,0x3303000000LL,0x800842093c0LL,0x3c078a3883c0LL,0x4093c9146180LL,0x1c82072081c0LL,0x381000001380LL,0x1c82082081c0LL,0x3c10470413c0LL,0x410470413c0LL,0x38920c001380LL,0x20820f208200LL,0x3c20820823c0LL,0xc41041041c0LL,0x204081084200LL,0x3c1041041040LL,0x20a28b34d200LL,0x20c30a2c9200LL,0x1c82082081c0LL,0x72081c0LL,0x181c82082081c0LL,0x2040831040c0LL,0x1c8206041380LL,0x820820823c0LL,0x1c8208208200LL,0x86149248400LL,0x1451ca28a200LL,0x409184189400LL,0x82082145200LL,0x3c00421083c0LL,0xe08208208208eLL,0x10208102081040LL,0x7104104104107LL,0x8145142080LL,0x1f000000000000LL,0x102LL,0x7c93881c0000LL,0x1c8209180000LL,0x3c00003c0000LL,0x2cc2083c8208LL,0x3c03c81c0000LL,0x820823c208cLL,0x1c82cc2083c0000LL,0x208209380000LL,0x1041041c0004LL,0xc41041041c0004LL,0x2450c5241041LL,0x82082082083LL,0x28a28a3c0000LL,0x208209380000LL,0x1c82081c0000LL,0x1c8209180000LL,0x2082cc2083c0000LL,0x4104b340000LL,0x1c8181380000LL,0x3020823c2080LL,0x2cc208200000LL,0x85145200000LL,0x249596480000LL,0x205085200000LL,0x42186249400000LL,0x3c10843c0000LL,0xe08208108208eLL,0x2082082082082LL,0x7104108104107LL,0x713000000LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x7df7df7df7df7dfLL,0x7df75f75d75d75fLL,0x7df7df7df7da69aLL,0x7df75d41a01555fLL,0x7dd61555971d41dLL,0x7df5ca55969539fLL,0x7df41324c61a75fLL,0x7df7df7df7dd75dLL,0x7c76dd75d75d6c7LL,0x7de75b6db6db75eLL,0x7df7df7da71275fLL,0x7df75d41d75f7dfLL,0x75b6597df7df7dfLL,0x7df7df7d07df7dfLL,0x7df6597df7df7dfLL,0x7df79e7596d75cfLL,0x7df6175d75d761fLL,0x7df41d75d75d71fLL,0x7df41e75b5d761fLL,0x7df6175d95d741fLL,0x7df6db41b6996dfLL,0x7df6175d879e41fLL,0x7df6175997de45fLL,0x7df79e75d6d741fLL,0x7df6175d86d761fLL,0x7df71b5d05d761fLL,0x7df6597d965f7dfLL,0x75b6597d965f7dfLL,0x7df5d97995df7dfLL,0x7df7c07c07df7dfLL,0x7df7dc4dc7df7dfLL,0x7df75f75b5d641fLL,0x7df41f05545741fLL,0x7df3d641669965fLL,0x7df6175d85d761fLL,0x7df45e7df7de45fLL,0x7df6175d75d761fLL,0x7df41e79879e41fLL,0x7df79e79879e41fLL,0x7df4565d37de45fLL,0x7df5d75d05d75dfLL,0x7df41d75d75d41fLL,0x7df71b6db6db61fLL,0x7df5db75e75b5dfLL,0x7df41e79e79e79fLL,0x7df5d55544925dfLL,0x7df5d34d55165dfLL,0x7df6175d75d761fLL,0x7df7df7d85d761fLL,0x7c76175d75d761fLL,0x7df5db75c6db71fLL,0x7df6175d979e45fLL,0x7df75d75d75d41fLL,0x7df6175d75d75dfLL,0x7df7596965973dfLL,0x7df69a6155555dfLL,0x7df3d665b6563dfLL,0x7df75d75d69a5dfLL,0x7df41f79d6d741fLL,0x7d175d75d75d751LL,0x7cf5d76dd75e79fLL,0x7d86db6db6db6d8LL,0x7df7d769a69d75fLL,0x7c07df7df7df7dfLL,0x7df7df7df7df6ddLL,0x7df01645761f7dfLL,0x7df6175d665f7dfLL,0x7df41f7df41f7dfLL,0x7df5135d74175d7LL,0x7df41f41761f7dfLL,0x7df75d75d41d753LL,0x6175135d741f7dfLL,0x7df5d75d645f7dfLL,0x7df6db6db61f7dbLL,0x71b6db6db61f7dbLL,0x7df59a71a59e79eLL,0x7df75d75d75d75cLL,0x7df55555541f7dfLL,0x7df5d75d645f7dfLL,0x7df6175d761f7dfLL,0x7df6175d665f7dfLL,0x5d75135d741f7dfLL,0x7df79e79449f7dfLL,0x7df61765e45f7dfLL,0x7df4dd75d41d75fLL,0x7df5135d75df7dfLL,0x7df75a69a5df7dfLL,0x7df59624935f7dfLL,0x7df5da75a5df7dfLL,0x79d6595963df7dfLL,0x7df41e75b41f7dfLL,0x7d175d75e75d751LL,0x7dd75d75d75d75dLL,0x7d86db6d76db6d8LL,0x7df7df0cc7df7dfLL,0x7df7df7df7df7dfLL};
  const i64 FBMP4[256] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0x200208208200LL,0x14514LL,0x28af94f28a00LL,0x87a8a1838af08LL,0x894a1852a100LL,0xf3268c714200LL,0x8208LL,0x20408208208420LL,0x6210410410206LL,0x14336200LL,0x208f88200000LL,0x210618000000000LL,0x3c000000LL,0x618000000000LL,0x2104218420800LL,0x7228a28a2700LL,0xf8820820a300LL,0xf04210820700LL,0x720818820f00LL,0x410f92518400LL,0x72081c104f00LL,0x72299a084e00LL,0x104208420f00LL,0x72289c4a2700LL,0x39083c8a2700LL,0x618018600000LL,0x210618018600000LL,0x818198800000LL,0x3e03e000000LL,0x8cc0c080000LL,0x200210824f00LL,0xf02eaaea2f00LL,0xa4f24518600LL,0x7a289e8a2780LL,0xe04082084e00LL,0x7a28a28a2780LL,0xf0411c104f00LL,0x10411c104f00LL,0xe248b2084e00LL,0x8a28be8a2880LL,0xf88208208f80LL,0x310410410700LL,0x892286292880LL,0xf04104104100LL,0x8aaaaedb6880LL,0x8b2caaba6880LL,0x7228a28a2700LL,0x8209e8a2780LL,0x207228a28a2700LL,0x89228e492380LL,0x720818104e00LL,0x208208208f80LL,0x7228a28a2880LL,0x218524922080LL,0x5147aaaaa880LL,0xa4610624080LL,0x208208514880LL,0xf82108420f80LL,0x38208208208238LL,0x820408204102LL,0x1c41041041041cLL,0x22514508200LL,0x3e000000000000LL,0x408LL,0xf24e20700000LL,0x7a28a6682082LL,0xf02082f00000LL,0xb328a2f20820LL,0xf02fa2700000LL,0x208208f08230LL,0x720b328a2f00000LL,0x8a28a6e82082LL,0x410410700010LL,0x390410410700010LL,0x914314904104LL,0x20820820820eLL,0xaaaaaaf80000LL,0x8a28a6e80000LL,0x7228a2700000LL,0x827a28a6680000LL,0x820b328a2f00000LL,0x10412cd00000LL,0x720604e00000LL,0xc08208f08200LL,0xbb28a2880000LL,0x214514880000LL,0x92469a280000LL,0x894214880000LL,0x188618924080000LL,0xf84210f80000LL,0x38208204208238LL,0x8208208208208LL,0x1c41042041041cLL,0xc8e000000LL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x0LL,0xfbefbefbefbefbeLL,0xfbedbedb6db6dbeLL,0xfbefbefbefaaaaaLL,0xfbed3402a0965beLL,0xfb68165a6c340b6LL,0xfbe72a5a6a94ebeLL,0xfbe08c9328aadbeLL,0xfbefbefbefb6db6LL,0xf9ebb6db6db6b9eLL,0xfb8daebaebaedb8LL,0xfbefbefaac88dbeLL,0xfbedb6036dbefbeLL,0xdae9a6fbefbefbeLL,0xfbefbef82fbefbeLL,0xfbe9a6fbefbefbeLL,0xfbcebada6b9e7beLL,0xfbe89c71c71c8beLL,0xfbe036db6db4cbeLL,0xfbe0badae79e8beLL,0xfbe89e7a679e0beLL,0xfbebae02caa6bbeLL,0xfbe89e7a2eba0beLL,0xfbe89c624f3a1beLL,0xfbeebadb6b9e0beLL,0xfbe89c722b1c8beLL,0xfbec2e78271c8beLL,0xfbe9a6fa69befbeLL,0xdae9a6fa69befbeLL,0xfbe7a6e267befbeLL,0xfbef80f80fbefbeLL,0xfbef323b2f3efbeLL,0xfbedbedae79a0beLL,0xfbe0bc11411c0beLL,0xfbef1a09aaa69beLL,0xfbe81c72071c83eLL,0xfbe1baf3cf3a1beLL,0xfbe81c71c71c83eLL,0xfbe0baea2eba0beLL,0xfbeebaea2eba0beLL,0xfbe19a70cf3a1beLL,0xfbe71c70071c73eLL,0xfbe036db6db603eLL,0xfbecaebaebae8beLL,0xfbe72cd38d2c73eLL,0xfbe0baebaebaebeLL,0xfbe71451020873eLL,0xfbe70c31441873eLL,0xfbe89c71c71c8beLL,0xfbef3cf2071c83eLL,0xf9e89c71c71c8beLL,0xfbe72cd30b2cc3eLL,0xfbe89e7a6eba1beLL,0xfbedb6db6db603eLL,0xfbe89c71c71c73eLL,0xfbeda6a9a69cf3eLL,0xfbeaaa81451473eLL,0xfbef1a9ae99af3eLL,0xfbedb6db6aaa73eLL,0xfbe03ceb6b9e03eLL,0xf86db6db6db6d86LL,0xfbe79ebb6dbaebcLL,0xfa2baebaebaeba2LL,0xfbef9caaaab6dbeLL,0xf80fbefbefbefbeLL,0xfbefbefbefbebb6LL,0xfbe09a19e8befbeLL,0xfbe81c71893cf3cLL,0xfbe0bcf3c0befbeLL,0xfbe48c71c09e79eLL,0xfbe0bc01c8befbeLL,0xfbedb6db60b6d8eLL,0x89e48c71c0befbeLL,0xfbe71c71813cf3cLL,0xfbebaebae8befaeLL,0xc2ebaebae8befaeLL,0xfbe6aacaa6baebaLL,0xfbedb6db6db6db0LL,0xfbe51451403efbeLL,0xfbe71c71813efbeLL,0xfbe89c71c8befbeLL,0xf3c81c71893efbeLL,0x79e48c71c0befbeLL,0xfbeebae922befbeLL,0xfbe89e9ba1befbeLL,0xfbe3b6db60b6dbeLL,0xfbe40c71c73efbeLL,0xfbedaaaaa73efbeLL,0xfbe69a924d3efbeLL,0xfbe72adaa73efbeLL,0xe369a669af3efbeLL,0xfbe03adae03efbeLL,0xf86db6dbadb6d86LL,0xfb6db6db6db6db6LL,0xfa2baeb9ebaeba2LL,0xfbefbe330fbefbeLL,0xfbefbefbefbefbeLL};
  const int FPOP [190] = {0,6,6,20,21,16,20,3,11,11,9,9,6,4,4,10,16,13,12,13,14,14,16,10,17,16,8,10,8,12,8,10,23,16,20,11,18,15,12,15,17,15,10,14,10,22,20,16,15,18,16,12,11,15,13,19,13,10,15,13,9,13,10,6,2,14,17,11,17,15,12,18,16,8,12,13,10,17,13,12,16,16,9,10,11,13,9,15,9,13,13,13,9,13,8,
                          60,54,54,40,39,44,40,57,49,49,51,51,54,56,56,50,44,47,48,47,46,46,44,50,43,44,52,50,52,48,52,50,37,44,40,49,42,45,48,45,43,45,50,46,50,38,40,44,45,42,44,48,49,45,47,41,47,50,45,47,51,47,50,54,58,46,43,49,43,45,48,42,44,52,48,47,50,43,47,48,44,44,51,50,49,47,51,45,51,47,47,47,51,47,52};
  const int FBIN [ 11] = {0,10,12,14,17,37,44,46,48,51,61};
  const int FBINN[ 10] = {37,57,58,58,54,50,51,58,61,44};
  const int FBINI[ 10][61] = {{0x20,0x60,0x27,0x2d,0x2e,0x21,0x22,0x2c,0x5f,0x3a,0x3c,0x3e,0x69,0x7e,0x2a,0x2b,0x5c,0x72,0x76,0x78,0x7c,0x2f,0x37,0x3b,0x3f,0x4a,0x4c,0x59,0x5e,0x6c,0x73,0x28,0x29,0x43,0x54,0x63,0x74},
                              {0x20,0x60,0x27,0x2d,0x2e,0x21,0x22,0x2c,0x5f,0x3a,0x3c,0x3e,0x69,0x7e,0x2a,0x2b,0x5c,0x72,0x76,0x78,0x7c,0x2f,0x37,0x3b,0x3f,0x4a,0x4c,0x59,0x5e,0x6c,0x73,0x28,0x29,0x43,0x54,0x63,0x74,0x32,0x3d,0x46,0x53,0x66,0x6a,0x6f,0x31,0x33,0x56,0x58,0x5b,0x5d,0x6b,0x6e,0x75,0x79,0x7a,0x7b,0x7d},
                              {0x2f,0x37,0x3b,0x3f,0x4a,0x4c,0x59,0x5e,0x6c,0x73,0x28,0x29,0x43,0x54,0x63,0x74,0x32,0x3d,0x46,0x53,0x66,0x6a,0x6f,0x31,0x33,0x56,0x58,0x5b,0x5d,0x6b,0x6e,0x75,0x79,0x7a,0x7b,0x7d,0x34,0x35,0x4b,0x61,0x45,0x47,0x49,0x50,0x55,0x5a,0x65,0x77,0x25,0x30,0x36,0x39,0x41,0x4f,0x52,0x68,0x70,0x71},
                              {0x32,0x3d,0x46,0x53,0x66,0x6a,0x6f,0x31,0x33,0x56,0x58,0x5b,0x5d,0x6b,0x6e,0x75,0x79,0x7a,0x7b,0x7d,0x34,0x35,0x4b,0x61,0x45,0x47,0x49,0x50,0x55,0x5a,0x65,0x77,0x25,0x30,0x36,0x39,0x41,0x4f,0x52,0x68,0x70,0x71,0x38,0x48,0x62,0x64,0x6d,0x44,0x51,0x67,0x57,0x23,0x26,0x42,0x4e,0x24,0x4d,0x40},
                              {0x34,0x35,0x4b,0x61,0x45,0x47,0x49,0x50,0x55,0x5a,0x65,0x77,0x25,0x30,0x36,0x39,0x41,0x4f,0x52,0x68,0x70,0x71,0x38,0x48,0x62,0x64,0x6d,0x44,0x51,0x67,0x57,0x23,0x26,0x42,0x4e,0x24,0x4d,0x40,0xc0,0xcd,0xa4,0xa3,0xa6,0xc2,0xce,0xd7,0xc4,0xd1,0xe7,0xb8,0xc8,0xe2,0xe4,0xed},
                              {0x38,0x48,0x62,0x64,0x6d,0x44,0x51,0x67,0x57,0x23,0x26,0x42,0x4e,0x24,0x4d,0x40,0xc0,0xcd,0xa4,0xa3,0xa6,0xc2,0xce,0xd7,0xc4,0xd1,0xe7,0xb8,0xc8,0xe2,0xe4,0xed,0xa5,0xb0,0xb6,0xb9,0xc1,0xcf,0xd2,0xe8,0xf0,0xf1,0xc5,0xc7,0xc9,0xd0,0xd5,0xda,0xe5,0xf7},
                              {0xc0,0xcd,0xa4,0xa3,0xa6,0xc2,0xce,0xd7,0xc4,0xd1,0xe7,0xb8,0xc8,0xe2,0xe4,0xed,0xa5,0xb0,0xb6,0xb9,0xc1,0xcf,0xd2,0xe8,0xf0,0xf1,0xc5,0xc7,0xc9,0xd0,0xd5,0xda,0xe5,0xf7,0xb4,0xb5,0xcb,0xe1,0xb1,0xb3,0xd6,0xd8,0xdb,0xdd,0xeb,0xee,0xf5,0xf9,0xfa,0xfb,0xfd},
                              {0xa5,0xb0,0xb6,0xb9,0xc1,0xcf,0xd2,0xe8,0xf0,0xf1,0xc5,0xc7,0xc9,0xd0,0xd5,0xda,0xe5,0xf7,0xb4,0xb5,0xcb,0xe1,0xb1,0xb3,0xd6,0xd8,0xdb,0xdd,0xeb,0xee,0xf5,0xf9,0xfa,0xfb,0xfd,0xb2,0xbd,0xc6,0xd3,0xe6,0xea,0xef,0xa8,0xa9,0xc3,0xd4,0xe3,0xf4,0xaf,0xb7,0xbb,0xbf,0xca,0xcc,0xd9,0xde,0xec,0xf3},
                              {0xb4,0xb5,0xcb,0xe1,0xb1,0xb3,0xd6,0xd8,0xdb,0xdd,0xeb,0xee,0xf5,0xf9,0xfa,0xfb,0xfd,0xb2,0xbd,0xc6,0xd3,0xe6,0xea,0xef,0xa8,0xa9,0xc3,0xd4,0xe3,0xf4,0xaf,0xb7,0xbb,0xbf,0xca,0xcc,0xd9,0xde,0xec,0xf3,0xaa,0xab,0xdc,0xf2,0xf6,0xf8,0xfc,0xba,0xbc,0xbe,0xe9,0xfe,0xa1,0xa2,0xac,0xdf,0xad,0xae,0xa7,0xe0,0xa0},
                              {0xb2,0xbd,0xc6,0xd3,0xe6,0xea,0xef,0xa8,0xa9,0xc3,0xd4,0xe3,0xf4,0xaf,0xb7,0xbb,0xbf,0xca,0xcc,0xd9,0xde,0xec,0xf3,0xaa,0xab,0xdc,0xf2,0xf6,0xf8,0xfc,0xba,0xbc,0xbe,0xe9,0xfe,0xa1,0xa2,0xac,0xdf,0xad,0xae,0xa7,0xe0,0xa0}};
  const i64 FMASK = 0xfffffffffffffffLL; // asc font
  const uch ABLACK = 0, AWHITE = 215, CBLACK = 0xa0, CWHITE = 0x20;
  const int FROWS = 10, FCOLS = 6, TBUF_MAXSIZE = 1600 * 1200, HEADER_SIZE = 8;

  inline int popcount60(i64 aa) {
    aa -= ((aa >> 1) & 0x0555555555555555LL); // count 2bits
    aa = (((aa >> 2) & 0x0333333333333333LL) + (aa & 0x0333333333333333LL)); // count 4bits
    aa = (((aa >> 4) + aa) & 0x0f0f0f0f0f0f0f0fLL); // count 8bits
    aa += (aa >> 8); // count 16bits
    aa += (aa >> 16); // count 32bits
    aa += (aa >> 32); // count 64bits
    aa &= 0x7f;
    return aa;
  }

  uch itp(i64 block, int plaintxt, int wmatch, int wmismatch) { // main algorithm - interpolate 64bit block -> ascii chr
    if (! block) return CWHITE; // white
    if (block == FMASK) return plaintxt ? '@' : CBLACK; // black
    int ii, jj, pp = popcount60(block), *fbmpi, wmax; uch chr = 0;
    for (ii = 0; ! (FBIN[ii] <= pp && pp < FBIN[ii + 1]); ii ++); // find fbin
    if (plaintxt && ii > 5) ii = 5;
    for (jj = FBINN[ii], fbmpi = (int *) FBINI[ii], wmax = -0x80000000; jj --; fbmpi ++) {
      pp  = popcount60(block & FBMP0[*fbmpi]) *    wmatch;
      pp -= popcount60(block ^ FBMP0[*fbmpi]) * wmismatch;
      pp += popcount60(block & FBMP1[*fbmpi]);
      pp += popcount60(block & FBMP2[*fbmpi]);
      pp += popcount60(block & FBMP3[*fbmpi]);
      pp += popcount60(block & FBMP4[*fbmpi]);
      if (pp > wmax && (!plaintxt || *fbmpi < 0x80)) { chr = *fbmpi; wmax = pp; }
    }
    return chr;
  }

  inline uch rgb2palette(uch *rgb) { return (((int) rgb[0] * 6) >> 8) * 36 + (((int) rgb[1] * 6) >> 8) * 6 + (((int) rgb[2] * 6) >> 8); }

  inline int rgb2bw(uch *rgb, int *derr0, int *derr1) {
    int gray = 54 * (int) rgb[0] + 183 * (int) rgb[1] + 19 * (int) rgb[2] + derr0[0]; // poynton gray cff
    int _derr = gray < 0x8000 ? gray : gray - 0x10000; // dither err
    derr0[ 1] += (7 * _derr) >> 4; // floyd-steinberg dither cff
    derr1[-1] += (3 * _derr) >> 4;
    derr1[ 0] += (5 * _derr) >> 4;
    derr1[ 1] += (    _derr) >> 4;
    return gray < 0x8000;
  }



  //// ansi term
  uch *ansi_check(PyObject *barr, int *TROWS, int *TCOLS) {
    if (! PyByteArray_Check(barr)) throw pyerr(PyExc_TypeError, "not bytearray object");
    if (PYLENGTH(barr) < HEADER_SIZE) throw pyerr(PyExc_IndexError, "bytearray size must be at least %i bytes", HEADER_SIZE);
    uch *ss = (uch *) PyByteArray_AS_STRING(barr); *TROWS = ss[0] * 256 + ss[1], *TCOLS = ss[2] * 256 + ss[3]; ss += HEADER_SIZE;
    if (*TROWS * *TCOLS > TBUF_MAXSIZE) throw pyerr(PyExc_IndexError, "img too big");
    if (PYLENGTH(barr) != HEADER_SIZE + *TROWS * *TCOLS * 2) throw pyerr(PyExc_IndexError, "bytearray size does not match image dimensions %i x %i", *TROWS, *TCOLS);
    for (int ii = *TROWS * *TCOLS; ii --; ss += 2) {
      if (ss[0] >= 216) throw pyerr(PyExc_ValueError, "invalid color");
      if (ss[1] < 0x20 || (0x7f <= ss[1] && ss[1] < 0xa0) || 0xff <= ss[1]) throw pyerr(PyExc_ValueError, "invalid chr");
    }
    return ss - *TROWS * *TCOLS * 2;
  }

  inline int ansi_reset(uch *ss) { return sprintf((char *) ss, "\033[0m"); }

  inline int ansi_chr(uch *ss, uch *chr) { return sprintf((char *) ss, chr[1] & 128 ? "\033[97;48;5;%im%c" : "\033[107;38;5;%im%c", chr[0] + 16, chr[1] & 127); }

  PyObject *ansi_str(PyObject *self, PyObject *barr) {
    try {
      int TROWS, TCOLS, ii, jj, color, color0;
      uch *aa = ansi_check(barr, &TROWS, &TCOLS), ss[TROWS * (TCOLS * 16 + 1) + 1], *bb = ss;
      for (ii = TROWS * TCOLS; ii; bb += sprintf((char *) bb, "\033[0m\n"))
        for (color0 = 0, jj = TCOLS; jj --; ii --, aa += 2, color0 = color) {
          color = (aa[1] & 128) * 256 + aa[0] + 16;
          if (color == color0) { *bb = aa[1] & 127; bb ++; } // shortcut - ignore duplicate color
          else bb += ansi_chr(bb, aa);
        }
      return PyUnicode_FromStringAndSize((char *) ss, bb + ansi_reset(bb) - ss);
    }
    catch (...) { return NULL; }
  }



  //// png io
  const png_color PNG_PALETTE216[216] = {{0,0,0},{0,0,51},{0,0,102},{0,0,153},{0,0,204},{0,0,255},{0,51,0},{0,51,51},{0,51,102},{0,51,153},{0,51,204},{0,51,255},{0,102,0},{0,102,51},{0,102,102},{0,102,153},{0,102,204},{0,102,255},{0,153,0},{0,153,51},{0,153,102},{0,153,153},{0,153,204},{0,153,255},{0,204,0},{0,204,51},{0,204,102},{0,204,153},{0,204,204},{0,204,255},{0,255,0},{0,255,51},{0,255,102},{0,255,153},{0,255,204},{0,255,255},{51,0,0},{51,0,51},{51,0,102},{51,0,153},{51,0,204},{51,0,255},{51,51,0},{51,51,51},{51,51,102},{51,51,153},{51,51,204},{51,51,255},{51,102,0},{51,102,51},{51,102,102},{51,102,153},{51,102,204},{51,102,255},{51,153,0},{51,153,51},{51,153,102},{51,153,153},{51,153,204},{51,153,255},{51,204,0},{51,204,51},{51,204,102},{51,204,153},{51,204,204},{51,204,255},{51,255,0},{51,255,51},{51,255,102},{51,255,153},{51,255,204},{51,255,255},{102,0,0},{102,0,51},{102,0,102},{102,0,153},{102,0,204},{102,0,255},{102,51,0},{102,51,51},{102,51,102},{102,51,153},{102,51,204},{102,51,255},{102,102,0},{102,102,51},{102,102,102},{102,102,153},{102,102,204},{102,102,255},{102,153,0},{102,153,51},{102,153,102},{102,153,153},{102,153,204},{102,153,255},{102,204,0},{102,204,51},{102,204,102},{102,204,153},{102,204,204},{102,204,255},{102,255,0},{102,255,51},{102,255,102},{102,255,153},{102,255,204},{102,255,255},{153,0,0},{153,0,51},{153,0,102},{153,0,153},{153,0,204},{153,0,255},{153,51,0},{153,51,51},{153,51,102},{153,51,153},{153,51,204},{153,51,255},{153,102,0},{153,102,51},{153,102,102},{153,102,153},{153,102,204},{153,102,255},{153,153,0},{153,153,51},{153,153,102},{153,153,153},{153,153,204},{153,153,255},{153,204,0},{153,204,51},{153,204,102},{153,204,153},{153,204,204},{153,204,255},{153,255,0},{153,255,51},{153,255,102},{153,255,153},{153,255,204},{153,255,255},{204,0,0},{204,0,51},{204,0,102},{204,0,153},{204,0,204},{204,0,255},{204,51,0},{204,51,51},{204,51,102},{204,51,153},{204,51,204},{204,51,255},{204,102,0},{204,102,51},{204,102,102},{204,102,153},{204,102,204},{204,102,255},{204,153,0},{204,153,51},{204,153,102},{204,153,153},{204,153,204},{204,153,255},{204,204,0},{204,204,51},{204,204,102},{204,204,153},{204,204,204},{204,204,255},{204,255,0},{204,255,51},{204,255,102},{204,255,153},{204,255,204},{204,255,255},{255,0,0},{255,0,51},{255,0,102},{255,0,153},{255,0,204},{255,0,255},{255,51,0},{255,51,51},{255,51,102},{255,51,153},{255,51,204},{255,51,255},{255,102,0},{255,102,51},{255,102,102},{255,102,153},{255,102,204},{255,102,255},{255,153,0},{255,153,51},{255,153,102},{255,153,153},{255,153,204},{255,153,255},{255,204,0},{255,204,51},{255,204,102},{255,204,153},{255,204,204},{255,204,255},{255,255,0},{255,255,51},{255,255,102},{255,255,153},{255,255,204},{255,255,255}};
#define IROWS (TROWS * FROWS)
#define ICOLS (TCOLS * FCOLS)
#define IROWBYTES (ICOLS * 3)

  inline void png_close(FILE *FP, png_structp PNG_READ, png_structp PNG_WRITE, png_infop PNG_INFO) {
    if (PNG_READ) png_destroy_read_struct(&PNG_READ, &PNG_INFO, NULL);
    if (PNG_WRITE) png_destroy_write_struct(&PNG_WRITE, &PNG_INFO);
    if (FP) fclose(FP);
  }

  PyObject *png_read(PyObject *self, PyObject *args) {
    char *fpath, *dpath = NULL; int scale, plaintxt, wmatch, wmismatch; if (! PyArg_ParseTuple(args, "siiii|s:png_read", &fpath, &scale, &plaintxt, &wmatch, &wmismatch, &dpath)) return NULL;
    FILE *FP = NULL; png_structp PNG_READ = NULL; png_infop PNG_INFO = NULL;
    FILE *DP = NULL; png_structp PNG_DWRITE = NULL; png_infop PNG_DINFO = NULL;
    try {



      // png init
      if (scale < 1) throw pyerr(PyExc_ValueError, "scale must be >= 1");
      if (! (FP = fopen(fpath, "rb"))) throw pyerr(PyExc_IOError, "cannot open <%s>", fpath);
      uch header[HEADER_SIZE]; if ((uint) HEADER_SIZE != fread(header, 1, HEADER_SIZE, FP)) throw pyerr(PyExc_IOError, "fail fread header");
      if (! png_check_sig(header, HEADER_SIZE)) throw pyerr(PyExc_IOError, "fail png_check_sig");
      if (! (PNG_READ = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL)) || ! (PNG_INFO = png_create_info_struct(PNG_READ))) throw pyerr(PyExc_IOError, "fail create_struct");
      if (setjmp(png_jmpbuf(PNG_READ))) throw pyerr(PyExc_IOError, "callback err");
      png_init_io(PNG_READ, FP); // init io
      png_set_sig_bytes(PNG_READ, HEADER_SIZE); // seek offset
      png_read_info(PNG_READ, PNG_INFO); // read img
      int TROWS = (PNG_INFO -> height * scale + FROWS - 1) / FROWS, TCOLS = (PNG_INFO -> width * scale + FCOLS - 1) / FCOLS; if (TROWS * TCOLS > TBUF_MAXSIZE) throw pyerr(PyExc_IndexError, "img too big");
      if (PNG_INFO -> color_type == PNG_COLOR_TYPE_PALETTE) png_set_expand(PNG_READ); // palette -> rgb
      if (PNG_INFO -> color_type == PNG_COLOR_TYPE_GRAY && PNG_INFO -> bit_depth < 8) png_set_expand(PNG_READ); // gray 1/2/4bit -> gray 8bit
      if (png_get_valid(PNG_READ, PNG_INFO, PNG_INFO_tRNS)) png_set_expand(PNG_READ); // transparency -> rgba
      if (PNG_INFO -> bit_depth == 16) png_set_strip_16(PNG_READ); // 16bit -> 8bit
      if (PNG_INFO -> color_type == PNG_COLOR_TYPE_GRAY || PNG_INFO -> color_type == PNG_COLOR_TYPE_GRAY_ALPHA) png_set_gray_to_rgb(PNG_READ); // gray -> rgb
      png_read_update_info(PNG_READ, PNG_INFO); // update rgb format



      if (dpath) { // debug
        if (! (DP = fopen(dpath, "wb"))) throw pyerr(PyExc_IOError, "cannot open <%s>", dpath);
        if (! (PNG_DWRITE = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL)) || ! (PNG_DINFO = png_create_info_struct(PNG_DWRITE))) throw pyerr(PyExc_IOError, "fail create_struct");
        if (setjmp(png_jmpbuf(PNG_DWRITE))) throw pyerr(PyExc_IOError, "callback err");
        png_init_io(PNG_DWRITE, DP); // init io
        png_set_IHDR(PNG_DWRITE, PNG_DINFO, ICOLS, IROWS, 8, PNG_COLOR_TYPE_PALETTE, PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT); // png header
        png_set_PLTE(PNG_DWRITE, PNG_DINFO, (png_colorp) PNG_PALETTE216, 216); // set palette216
        png_write_info(PNG_DWRITE, PNG_DINFO); // write header
      }



      int row, col, ii, jj, kk;
      uch RGB_BUF[IROWBYTES]; for (ii = IROWBYTES; ii --;) RGB_BUF[ii] = 0;
      int derrs[2][ICOLS + 2], *derr0 = derrs[0] + 1, *derr1 = derrs[1] + 1, *derr2; for (ii = ICOLS + 2; ii --;) derr0[ii] = derr1[ii] = 0;
      i64 blocks[TCOLS], *block, shift; PyObject *barr = PyByteArray_FromStringAndSize(NULL, HEADER_SIZE + TROWS * TCOLS * 2); if (!barr) throw pyerr(PyExc_MemoryError, "fail new bytearray"); uch *arr = (uch *) PyByteArray_AS_STRING(barr); arr[0] = TROWS >> 8; arr[1] = TROWS & 255; arr[2] = TCOLS >> 8; arr[3] = TCOLS & 255; arr += HEADER_SIZE;
      for (row = 0; row < IROWS; arr += TCOLS * 2) {
        for (ii = TCOLS; ii --;) blocks[ii] = 0; // wipe blocks



        for (shift = 1, ii = FROWS; ii --; row ++, shift <<= FCOLS) { // loop FROWS
          if ((uint) row < PNG_INFO -> height * scale && ! (row % scale)) { // scale row
            png_read_row(PNG_READ, RGB_BUF, NULL); // read row
            if (scale > 1) // scale col
              for (jj = ICOLS / scale; jj --;)
                for (kk = scale; kk --;) {
                  RGB_BUF[(jj * scale + kk) * 3    ] = RGB_BUF[jj * 3    ];
                  RGB_BUF[(jj * scale + kk) * 3 + 1] = RGB_BUF[jj * 3 + 1];
                  RGB_BUF[(jj * scale + kk) * 3 + 2] = RGB_BUF[jj * 3 + 2];
                }
          }
          SWAP(derr0, derr1, derr2); for (jj = ICOLS + 2; jj --;) derr1[jj - 1] = 0; // init dither buf
          for (block = blocks, col = 0; col < ICOLS; block ++, shift >>= FCOLS)
            for (jj = FCOLS; jj --; col ++, shift <<= 1)
              if (rgb2bw(RGB_BUF + col * 3, derr0 + col, derr1 + col)) *block |= shift; // rgb -> bw -> 64bit block
        }
        for (ii = TCOLS; ii --;) {
          arr[ii * 2    ] = rgb2palette(RGB_BUF + ii * FCOLS * 3); // save color data
          arr[ii * 2 + 1] = itp(blocks[ii], plaintxt, wmatch, wmismatch); // save itp data
        }



        if (dpath) { // debug
          for (shift = 1, ii = FROWS; ii --; shift <<= FCOLS) {
            for (jj = 0; jj < TCOLS; jj ++)
              for (kk = 0; kk < FCOLS; kk ++)
                RGB_BUF[jj * FCOLS + kk] = blocks[jj] & (shift << kk) ? ABLACK : AWHITE;
            png_write_row(PNG_DWRITE, RGB_BUF);
          }
        }



      }
      if (dpath) png_close(DP, NULL, PNG_DWRITE, PNG_DINFO);
      png_close(FP, PNG_READ, NULL, PNG_INFO); return barr;
    }
    catch (...) { png_close(FP, PNG_READ, NULL, PNG_INFO); return NULL; }
  };

  PyObject *png_write(PyObject *self, PyObject *args) {
    char *fpath; PyObject *barr; if (! PyArg_ParseTuple(args, "sO:png_write", &fpath, &barr)) return NULL;
    FILE *FP = NULL; png_structp PNG_WRITE = NULL; png_infop PNG_INFO = NULL;
    try {



      // png init
      int TROWS, TCOLS; uch *arr = ansi_check(barr, &TROWS, &TCOLS);
      if (! (FP = fopen(fpath, "wb"))) throw pyerr(PyExc_IOError, "cannot open <%s>", fpath);
      if (! (PNG_WRITE = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL)) || ! (PNG_INFO = png_create_info_struct(PNG_WRITE))) throw pyerr(PyExc_IOError, "fail create_struct");
      if (setjmp(png_jmpbuf(PNG_WRITE))) throw pyerr(PyExc_IOError, "callback err");
      png_init_io(PNG_WRITE, FP); // init io
      png_set_IHDR(PNG_WRITE, PNG_INFO, ICOLS, IROWS, 8, PNG_COLOR_TYPE_PALETTE, PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT); // png header
      png_set_PLTE(PNG_WRITE, PNG_INFO, (png_colorp) PNG_PALETTE216, 216); // set palette216
      png_write_info(PNG_WRITE, PNG_INFO); // write header



      int row, col, frow, fcol; uch PAL_BUF[FROWS][IROWBYTES]; i64 shift;
      for (row = IROWS; row;) {
        for (col = 0; col < ICOLS; col += FCOLS, arr += 2)
          for (shift = 1, frow = 0; frow < FROWS; frow ++)
            for (fcol = 0; fcol < FCOLS; fcol ++, shift <<= 1)
              PAL_BUF[frow][col + fcol] = FBMP0[arr[1]] & shift ? arr[0] : AWHITE;
        for (frow = 0; frow < FROWS; frow ++, row --) png_write_row(PNG_WRITE, PAL_BUF[frow]);
      }
      png_write_end(PNG_WRITE, PNG_INFO); png_close(FP, NULL, PNG_WRITE, PNG_INFO); Py_RETURN_NONE;
    }
    catch (...) { png_close(FP, NULL, PNG_WRITE, PNG_INFO); return NULL; }
  }
}







namespace MARRAY {
  typedef char      CC; const int code_CC = 'c'; const int enum_CC = 0;
  typedef long long II; const int code_II = 'i'; const int enum_II = 1;
  typedef double    FF; const int code_FF = 'f'; const int enum_FF = 2;
  inline PyObject *from_TT(CC aa) { return PyLong_FromLong    (aa); }
  inline PyObject *from_TT(II aa) { return PyLong_FromLongLong(aa); }
  inline PyObject *from_TT(FF aa) { return PyFloat_FromDouble (aa); }
  inline void as_TT(PyObject *aa, CC *words) { *words = PyLong_AsLong    (aa); if (*words == ERROR && PyErr_Occurred()) throw ERROR; }
  inline void as_TT(PyObject *aa, II *words) { *words = PyLong_AsLongLong(aa); if (*words == ERROR && PyErr_Occurred()) throw ERROR; }
  inline void as_TT(PyObject *aa, FF *words) { *words = PyFloat_AsDouble (aa); if (*words == ERROR && PyErr_Occurred()) throw ERROR; }
  inline void str_TT(CC aa, char *&ss) { ss += sprintf(ss, "%.2x ", aa & 0xff); }
  inline void str_TT(II aa, char *&ss) { static const int ll = 10 + 2; static const i64 mm = pow(10, ll - 2); ss += abs(aa) < mm ? sprintf(ss, "%*lli ", ll - 1, aa) : sprintf(ss, "%*.*e ", ll - 1, ll - 8, (double) aa); }
  inline void str_TT(FF aa, char *&ss) { static const int ll = 6 + 8; ss += sprintf(ss, "%*.*g ", ll - 1, ll - 8, aa); }
  PyGetSetDef GETSET[256]; PyMethodDef METHOD[256]; PySequenceMethods SEQUENCE = {NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL};
  PyTypeObject TYPE = {PyVarObject_HEAD_INIT(NULL, 0)"_marray",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  template <typename TT> class tarr; class marr { public: PyObject_HEAD; void *tself; };
  inline int marr_check(PyObject *self) { return PyObject_IsInstance(self, (PyObject *) &TYPE); }
  inline int tcode_from_args(PyObject *args) { args = PyTuple_GetItem(args, 0); if (! args) throw ERROR; int tcode = PyLong_AsLong(args); if (tcode == ERROR && PyErr_Occurred()) throw ERROR; return tcode; }



  //// template
#define TSIZE ((int) sizeof(TT))
#define LENGTH (shape0 * shape1)
#define BYTES (PyByteArray_AS_STRING(bytes))
#define TARR(TT, self) ((tarr<TT> *) ((marr *) self) -> tself)
#define ITERATE1(ii, jj) int ii, jj; for (ii = 0; ii < shape0; ii ++) for (jj = 0; jj < shape1; jj ++)
#define ITERATE2(i0, j0, i1, j1, tthem) int i0, j0, i1, j1, di = tthem -> shape0 == 1 ? 0 : 1, dj = tthem -> shape1 == 1 ? 0 : 1; for (i0 = 0, i1 = 0; i0 < shape0; i0 ++, i1 += di) for (j0 = 0, j1 = 0; j0 < shape1; j0 ++, j1 += dj)
  PyObject *__callmethod__(PyObject *self, PyObject *args);
  template <typename TT> class tarr {
  public:
    marr *self; int tcode; PyObject *bytes; TT *words;
    int shape0, shape1, strides0, strides1;
    inline ~tarr() { Py_DECREF(bytes); }
    inline tarr(PyTypeObject *type, int _tcode, PyObject *_bytes, TT *_words, int _shape0, int _shape1, int _strides0, int _strides1) {
      self = (marr *) type -> tp_alloc(type, 0); if (! self) throw ERROR;
      self -> tself = this;
      tcode = _tcode; bytes = _bytes; words = _words; shape0 = _shape0; shape1 = _shape1; strides0 = _strides0; strides1 = _strides1;
      Py_INCREF(bytes);
    }
    inline void marr_dealloc() { delete this; }
    inline static PyObject *marr_new(PyTypeObject *type, int tcode, PyObject *bytes, TT *words, int shape0, int shape1, int strides0, int strides1) {
      try { return (PyObject *) (new tarr(type, tcode, bytes, words, shape0, shape1, strides0, strides1)) -> self; }
      catch (bad_alloc&) { throw pyerr(PyExc_MemoryError, "fail new marray"); }
    }
    static PyObject *marr_new(PyTypeObject *type, PyObject *args) {
      int tcode; PyObject *bytes; if (! PyArg_ParseTuple(args, "iO:marr_new", &tcode, &bytes)) throw ERROR;
      if (! PyByteArray_Check(bytes)) throw pyerr(PyExc_TypeError, "not bytearray object");
      int ll = PYLENGTH(bytes); if (ll % TSIZE) throw pyerr(PyExc_IndexError, "bytearray size not multiple of tsize");
      ll /= TSIZE; return marr_new(type, tcode, bytes, (TT *) BYTES, 1, ll, ll, 1);
    }



    //// static method
    static PyObject *tsize_from_tcode(PyObject *args) { return PyLong_FromLong(TSIZE); }
    static PyObject *bytes_from_seq(PyObject *args) {
      int tcode; PyObject *seq; if (! PyArg_ParseTuple(args, "iO:bytes_from_seq", &tcode, &seq)) throw ERROR;
      PyObject *bytes = NULL, *itr = NULL, *aa = NULL;
      try {
        if (! PySequence_Check(seq)) throw pyerr(PyExc_TypeError, "not sequence object");
        bytes = PyByteArray_FromStringAndSize(NULL, PYLENGTH(seq) * TSIZE); if (! bytes) throw pyerr(PyExc_MemoryError, "fail new bytearray");
        itr = PyObject_GetIter(seq); if (! itr) throw ERROR;
        TT *words = (TT *) BYTES; for(; (aa = PyIter_Next(itr)); words ++) { as_TT(aa, words); Py_DECREF(aa); }
        return bytes;
      }
      catch (...) {
        if (aa) Py_DECREF(aa);
        if (itr) Py_DECREF(itr);
        if (bytes) Py_DECREF(bytes);
        throw;
      }
    }



    //// helper
    inline TT *offset(int ii, int jj) { return words + ii * strides0 + jj * strides1; }
    inline int idx0_check(int ii) { if ((ii < 0 ? ii += shape0 : ii) < 0 || shape0 <= ii) throw pyerr(PyExc_IndexError, "index[0] out of range"); return ii; }
    inline int idx1_check(int ii) { if ((ii < 0 ? ii += shape1 : ii) < 0 || shape1 <= ii) throw pyerr(PyExc_IndexError, "index[1] out of range"); return ii; }
    inline void mem_check() { if (words < (TT *) BYTES || offset(shape0 - 1, shape1 - 1) + 1 > (TT *) (BYTES + PYLENGTH(bytes))) throw pyerr(PyExc_MemoryError, "marray memory invalidated"); }
    inline int contiguous() { return strides1 == 1 && (TT *) BYTES == words; }
    inline int transposed() { return strides1 != 1; }
    inline tarr<TT> *tcode_check(PyObject *them) { if (TARR(TT, them) -> tcode != tcode) throw pyerr(PyExc_TypeError, "inconsistent tcode - self<%c> vs them<%c>", tcode, (TARR(TT, them)) -> tcode); return TARR(TT, them); }
    inline void dim_check(tarr<TT> *tthem) {
      if (tthem -> shape0 != 1 && tthem -> shape0 != shape0) throw pyerr(PyExc_IndexError, "inconsistent shape0 - self<%i> vs them<%i>", shape0, tthem -> shape0);
      if (tthem -> shape1 != 1 && tthem -> shape1 != shape1) throw pyerr(PyExc_IndexError, "inconsistent shape1 - self<%i> vs them<%i>", shape1, tthem -> shape1);
    }



    //// sequence
    int sq_length() { return LENGTH; }
    int sq_contains(PyObject *aa) { TT bb; as_TT(aa, &bb); ITERATE1(ii, jj) if (*offset(ii, jj) == bb) return true; return false; }
    PyObject *sq_item(int ii) { if (ii >= LENGTH) throw ERROR; return from_TT(*offset(ii / shape1, ii % shape1)); }



    //// attribute
    PyObject *get_bytes(PyObject *args) { Py_INCREF(bytes); return bytes; }
    PyObject *get_shape0(PyObject *args) { return PyLong_FromLong(shape0); }
    PyObject *get_shape1(PyObject *args) { return PyLong_FromLong(shape1); }
    PyObject *get_strides0(PyObject *args) { return PyLong_FromLong(strides0); }
    PyObject *get_strides1(PyObject *args) { return PyLong_FromLong(strides1); }
    PyObject *get_tcode(PyObject *args) { return PyUnicode_FromFormat("%c", tcode); }
    PyObject *get_tsize(PyObject *args) { return PyLong_FromLong(TSIZE); }
    PyObject *get_contiguous(PyObject *args) { return PyLong_FromLong(contiguous()); }
    PyObject *get_transposed(PyObject *args) { return PyLong_FromLong(transposed()); }
    PyObject *get_T(PyObject *args) { return marr_new(Py_TYPE(self), tcode, bytes, words, shape1, shape0, strides1, strides0); }



    //// method
    // PyObject *__contains__(PyObject *args) {
      // PyObject *aa; if (! PyArg_ParseTuple(args, "O:__contains__", &aa)) throw ERROR;
      // TT bb; as_TT(aa, &bb); ITERATE1(ii, jj) if (*offset(ii, jj) == bb) { Py_RETURN_FALSE; } Py_RETURN_TRUE; }
    PyObject *__copy__(PyObject *args) {
      PyTypeObject *type = NULL; if (! PyArg_ParseTuple(args, "|O:__copy__", &type)) throw ERROR;
      return marr_new(type ? type : Py_TYPE(self), tcode, bytes, words, shape0, shape1, strides0, strides1);
    }
    // PyObject *__len__(PyObject *args) { return PyLong_FromLong(LENGTH); }
    PyObject *reshape(PyObject *args) {
      int ll, mm; if (! PyArg_ParseTuple(args, "ii:reshape", &ll, &mm)) throw ERROR;
      if (! contiguous()) throw pyerr(PyExc_IndexError, "cannot reshape non-contiguous marray");
      if (ll == -1) ll = LENGTH / mm; else if (mm == -1) mm = LENGTH / ll;
      if (ll < 0 || ll * mm != LENGTH) throw pyerr(PyExc_IndexError, "invalid shape");
      return marr_new(Py_TYPE(self), tcode, bytes, words, ll, mm, mm, strides1);
    }
    inline void parse_slice(int ii, PyObject *slice, ssz &start, ssz &stop, ssz &step, ssz &slicelength) {
      if (PyLong_Check(slice)) { start = ii ? idx1_check(PyLong_AsLong(slice)) : idx0_check(PyLong_AsLong(slice)); stop = start + 1; step = 1; slicelength = 1; }
      else if (PySlice_Check(slice)) { if (PySlice_GetIndicesEx((PySliceObject *) slice, ii ? shape1 : shape0, &start, &stop, &step, &slicelength) == ERROR) throw ERROR; }
      else throw pyerr(PyExc_TypeError, "index[%i] not int/slice object", ii);
    }
    PyObject *__getitem__(PyObject *args) {
      int ii, jj; if (PyArg_ParseTuple(args, "ii:__getitem__", &ii, &jj)) { return from_TT(*offset(idx0_check(ii), idx1_check(jj))); } else { PyErr_Clear(); }
      PyObject *slice0 = NULL, *slice1 = NULL; if (! PyArg_ParseTuple(args, "O|O:__getitem__", &slice0, &slice1)) throw ERROR;
      ssz start0, stop0, step0, slicelength0; parse_slice(0, slice0, start0, stop0, step0, slicelength0);
      if (! slice1) return marr_new(Py_TYPE(self), tcode, bytes, offset(start0, 0), slicelength0, shape1, step0 * strides0, strides1);
      ssz start1, stop1, step1, slicelength1; parse_slice(1, slice1, start1, stop1, step1, slicelength1);
      return marr_new(Py_TYPE(self), tcode, bytes, offset(start0, start1), slicelength0, slicelength1, step0 * strides0, step1 * strides1);
    }
    // PyObject *__getitem___iter(PyObject *args) {
      // int ii; if (! PyArg_ParseTuple(args, "i:__getitem___iter", &ii)) throw ERROR;
      // if (ii >= LENGTH) throw pyerr(PyExc_StopIteration, NULL); return from_TT(*offset(ii / shape1, ii % shape1)); }
    void setslice(PyObject *aa) {
      if (! marr_check(aa)) { TT bb; as_TT(aa, &bb); ITERATE1(ii, jj) *offset(ii, jj) = bb; return; }
      tarr<TT> *tthem = tcode_check(aa); dim_check(tthem); ITERATE2(i0, j0, i1, j1, tthem) *offset(i0, j0) = *tthem -> offset(i1, j1);
    }
    PyObject *__setitem__(PyObject *args) {
      PyObject *slices, *aa; if (! PyArg_ParseTuple(args, "OO:__setitem__", &slices, &aa)) throw ERROR;
      int ii, jj; if (PyArg_ParseTuple(slices, "ii:__setitem__", &ii, &jj)) { as_TT(aa, offset(ii, jj)); Py_RETURN_NONE; } else { PyErr_Clear(); }
      PyObject *_self = __getitem__(slices);
      try { TARR(TT, _self) -> setslice(aa); Py_DECREF(_self); Py_RETURN_NONE; }
      catch (...) { Py_DECREF(_self); throw; }
    }
    PyObject *__str__(PyObject *args) {
      char ss[LENGTH * 16 + 1]; char *tt = ss; ITERATE1(ii, jj) str_TT(*offset(ii, jj), tt);
      return PyUnicode_FromStringAndSize(ss, tt - ss);
    }



    //// init
    static PyObject *marr_init(PyObject *module) {
#define METH_TT(rtype, fname, args, call, err) CLOSURE(rtype, fname, args, { try { switch (TARR(TT, self) -> tcode) { \
            case code_CC: TARR(CC, self) -> mem_check(); return TARR(CC, self) -> call; \
            case code_II: TARR(II, self) -> mem_check(); return TARR(II, self) -> call; \
            case code_FF: TARR(FF, self) -> mem_check(); return TARR(FF, self) -> call; \
            default: throw pyerr(PyExc_ValueError, "invalid tcode"); } } catch (...) { return err; } })
#define STATMETH_TT(rtype, fname, _args, call, err) CLOSURE(rtype, fname, _args, { try { switch (tcode_from_args(args)) { \
            case code_CC: return tarr<CC>::call;                        \
            case code_II: return tarr<II>::call;                        \
            case code_FF: return tarr<FF>::call;                        \
            default: throw pyerr(PyExc_ValueError, "invalid tcode"); } } catch (...) { return err; } })

      // sequence
      TYPE.tp_as_sequence = &SEQUENCE;
      METH_TT(int, sq_length, (PyObject *self), sq_length(), ERROR); SEQUENCE.sq_length = sq_length;
      METH_TT(int, sq_contains, (PyObject *self, PyObject *aa), sq_contains(aa), ERROR); SEQUENCE.sq_contains = sq_contains;
      METH_TT(PyObject *, sq_item, (PyObject *self, int ii), sq_item(ii), NULL); SEQUENCE.sq_item = sq_item;

      // method
#define METHOD(fname, sname) METH_TT(PyObject *, fname, (PyObject *self, PyObject *args), fname(args), NULL); METHOD[ii] = (PyMethodDef) {sname, fname, METH_VARARGS}; ii ++;
      int ii = 0; TYPE.tp_methods = METHOD;
      METHOD[ii] = (PyMethodDef) {"__callmethod__", MARRAY::__callmethod__, METH_VARARGS}; ii ++;

      // static method
#define STATICMETHOD(fname, sname) STATMETH_TT(PyObject *, fname, (PyObject *self, PyObject *args), fname(args), NULL); METHOD[ii] = (PyMethodDef) {sname, fname, METH_STATIC | METH_VARARGS}; ii ++;
      STATICMETHOD(tsize_from_tcode, "tsize_from_tcode");
      STATICMETHOD(bytes_from_seq, "bytes_from_seq");
      METHOD[ii] = (PyMethodDef) {NULL};

      // misc
      TYPE.tp_basicsize = sizeof(marr);
      METH_TT(void, marr_dealloc, (PyObject *self), marr_dealloc(), ); TYPE.tp_dealloc = marr_dealloc;
      STATMETH_TT(PyObject *, marr_new, (PyTypeObject *type, PyObject *args, PyObject *kwds), marr_new(type, args), NULL); TYPE.tp_new = marr_new;
      TYPE.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
      if (PyType_Ready(&TYPE) < 0) return NULL;
      Py_INCREF(&TYPE); PyModule_AddObject(module, "_marray", (PyObject *) &TYPE); return module;
    }
  };



  //// method caller
  PyObject *__callmethod__(PyObject *self, PyObject *_args) {
#define CALLMETH_TT(mname) switch (TARR(char, self) -> tcode) {         \
    case code_CC: TARR(CC, self) -> mem_check(); return TARR(CC, self) -> mname(args); \
    case code_II: TARR(II, self) -> mem_check(); return TARR(II, self) -> mname(args); \
    case code_FF: TARR(FF, self) -> mem_check(); return TARR(FF, self) -> mname(args); \
    default: throw pyerr(PyExc_ValueError, "invalid tcode"); }
#define CALLSTATMETH_TT(mname) CLOSURE(rtype, fname, _args, { try { switch (tcode_from_args(args)) { \
          case code_CC: return tarr<CC>::call;                          \
          case code_II: return tarr<II>::call;                          \
          case code_FF: return tarr<FF>::call;                          \
          default: throw pyerr(PyExc_ValueError, "invalid tcode"); } } catch (...) { return err; } })
    try {
      if (! marr_check(self)) throw pyerr(PyExc_TypeError, "self not marray object");
      const char *mname; PyObject *args; if (! PyArg_ParseTuple(_args, "sO:__callmethod__", &mname, &args)) throw ERROR;
      if (! PyTuple_Check(args)) throw pyerr(PyExc_TypeError, "args not tuple object");
      switch (*mname) {
      case '_':
        if (! strcmp(mname, "__copy__")) CALLMETH_TT(__copy__);
        if (! strcmp(mname, "__getitem__")) CALLMETH_TT(__getitem__);
        if (! strcmp(mname, "__setitem__")) CALLMETH_TT(__setitem__);
        if (! strcmp(mname, "__str__")) CALLMETH_TT(__str__);
        break;
      case 'g':
        if (! strcmp(mname, "get_bytes")) CALLMETH_TT(get_bytes);
        if (! strcmp(mname, "get_shape0")) CALLMETH_TT(get_shape0);
        if (! strcmp(mname, "get_shape1")) CALLMETH_TT(get_shape1);
        if (! strcmp(mname, "get_strides0")) CALLMETH_TT(get_strides0);
        if (! strcmp(mname, "get_strides1")) CALLMETH_TT(get_strides1);
        if (! strcmp(mname, "get_tcode")) CALLMETH_TT(get_tcode);
        if (! strcmp(mname, "get_tsize")) CALLMETH_TT(get_tsize);
        if (! strcmp(mname, "get_contiguous")) CALLMETH_TT(get_contiguous);
        if (! strcmp(mname, "get_transposed")) CALLMETH_TT(get_transposed);
        if (! strcmp(mname, "get_T")) CALLMETH_TT(get_T);
        break;
      case 'r':
        if (! strcmp(mname, "reshape")) CALLMETH_TT(reshape);
        break;
      case 's':
        break;
      }
      throw pyerr(PyExc_AttributeError, "'marray' object has no attribute '%s'", mname);
    }
    catch (...) { return NULL; }
  }
}







namespace numbytes {
  typedef MARRAY::tarr<char> MARRAY_TT;
  PyObject *is_itr(PyObject *self, PyObject *aa) { return PyLong_FromLong(    PyIter_Check(aa)); }
  PyObject *is_map(PyObject *self, PyObject *aa) { return PyLong_FromLong( PyMapping_Check(aa)); }
  PyObject *is_num(PyObject *self, PyObject *aa) { return PyLong_FromLong(  PyNumber_Check(aa)); }
  PyObject *is_seq(PyObject *self, PyObject *aa) { return PyLong_FromLong(PySequence_Check(aa)); }
  PyObject *refcnt(PyObject *self, PyObject *aa) { return PyLong_FromSsize_t(Py_REFCNT(aa)); }
  PyMethodDef module_method[] = {
    {"is_itr", is_itr, METH_O},
    {"is_map", is_map, METH_O},
    {"is_num", is_num, METH_O},
    {"is_seq", is_seq, METH_O},
    {"refcnt", refcnt, METH_O},
    {"png_read", IMG2TXT::png_read, METH_VARARGS},
    {"png_write", IMG2TXT::png_write, METH_VARARGS},
    {"ansi_str", IMG2TXT::ansi_str, METH_O},
    {NULL} // sentinel
  };

  struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_numbytes", // m_name
    NULL, // m_desc
    -1, // m_size
    module_method, // m_method
    NULL, // m_reload
    NULL, // m_traverse
    NULL, // m_clear
    NULL, // m_free
  };

  extern "C" {
    PyObject *PyInit__numbytes(void) {
      PyObject *module = PyModule_Create(&moduledef); if (! module) return NULL;
      if (! MARRAY_TT::marr_init(module)) return NULL;
      return module;
    }
  }
}
