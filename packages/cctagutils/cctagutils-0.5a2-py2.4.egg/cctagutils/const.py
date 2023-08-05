"""cctag library constants."""

__id__ = "$Id: const.py 722 2007-03-15 14:53:33Z nyergler $"
__version__ = "$Revision: 722 $"
__copyright__ = '(c) 2004, Creative Commons, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

import pkg_resources

def version():

	pkg_metadata = pkg_resources.get_provider("cctagutils")

	for line in pkg_metadata.get_metadata_lines("PKG-INFO"):
		if line.find('Version: ') == 0:
			return line.split()[-1].strip()

	return '-1'
	
TAG_MAP = {
	'UFI':'UFID',
	'BUF':'RBUF',
	'CNT':'PCNT',
	'COM':'COMM',
	'CRA':'AENC',
	'CRM':None, # ('bin','Encrypted meta frame')
	'EQU':'EQU2',
	'ETC':'ETCO',
	'GEO':'GEOB',
	'IPL':'IPLS',
	'LNK':'LINK',
	'MCI':'MCDI',
	'MLL':'MLLT',
	'PIC':'APIC',
	'POP':'POPM',
	'REV':'RVRB',
	'RVA':'RVA2',
	'STC':'SYTC',
	'SLT':'SYLT',
	'TAL':'TALB',
	'TBP':'TBPM',
	'TCM':'TCOM',
	'TCO':'TCON',
	'TCR':'TCOP',
	'TDA':'TDAT',
	'TDY':'TDLY',
	'TEN':'TENC',
	'TIM':'TIME',
	'TKE':'TKEY',
	'TLA':'TLAN',
	'TLE':'TLEN',
	'TMT':'TMED',
	'TP1':'TPE1',
	'TP2':'TPE2',
	'TP3':'TPE3',
	'TP4':'TPE4',
	'TPA':'TPOS',
	'TPB':'TPUB',
	'TOA':'TOPE',
	'TOF':'TOFN',
	'TOL':'TOLY',
	'TOR':'TORY',
	'TOT':'TOAL',
	'TRC':'TSRC',
	'TRD':'TRDA',
	'TRK':'TRCK',
	'TSI':'TSIZ',
	'TSS':'TSSE',
	'TT1':'TIT1',
	'TT2':'TIT2',
	'TT3':'TIT3',
	'TXT':'TEXT',
	'TYE':'TYER',
	'TXX':'TXXX',
	'ULT':'USLT',
	'WAF':'WOAF',
	'WAR':'WOAR',
	'WAS':'WOAS',
	'WCM':'WCOM',
	'WCP':'WCOP',
	'WPM':'WPUB',
	'WXX':'WXXX',
	}

