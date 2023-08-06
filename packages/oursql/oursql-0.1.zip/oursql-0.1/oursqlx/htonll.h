#ifdef _WIN32
#  include <winsock.h>
#else
#  include <arpa/inet.h>
#endif
#ifndef htonll
#  ifdef _WIN32
#    include <stdlib.h>
#    define ntohll _byteswap_uint64
#	 define htonll ntohll
#  else
#    ifdef _BIG_ENDIAN
#      define htonll(x)   (x)
#      define ntohll(x)   (x)
#    else
#      define htonll(x)   ((((uint64_t)htonl(x)) << 32) + htonl(x >> 32))
#      define ntohll(x)   ((((uint64_t)ntohl(x)) << 32) + ntohl(x >> 32))
#    endif
#  endif
#endif
