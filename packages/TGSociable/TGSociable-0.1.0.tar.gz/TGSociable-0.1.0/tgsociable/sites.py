import turbogears
all_sites = {
	'blinkbits': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blinkbits.png'),
		'url': 'http://www.blinkbits.com/bookmarklets/save.php?v=1&source_url=PERMALINK&title=TITLE&body=TITLE',
	},
	'BlinkList': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blinklist.png'),
		'url': 'http://www.blinklist.com/index.php?Action=Blink/addblink.php&Url=PERMALINK&Title=TITLE',
	},
	'BlogMemes': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blogmemes.png'),
		'url': 'http://www.blogmemes.net/post.php?url=PERMALINK&title=TITLE',
	},
	'BlogMemes Fr': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blogmemes.png'),
		'url': 'http://www.blogmemes.fr/post.php?url=PERMALINK&title=TITLE',
	},
	'BlogMemes Sp': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blogmemes.png'),
		'url': 'http://www.blogmemes.com/post.php?url=PERMALINK&title=TITLE',
	},
	'BlogMemes Cn': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blogmemes.png'),
		'url': 'http://www.blogmemes.cn/post.php?url=PERMALINK&title=TITLE',
	},
	'BlogMemes Jp': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blogmemes.png'),
		'url': 'http://www.blogmemes.jp/post.php?url=PERMALINK&title=TITLE',
	},
	'blogmarks': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blogmarks.png'),
		'url': 'http://blogmarks.net/my/new.php?mini=1&simple=1&url=PERMALINK&title=TITLE',
	},
	'blogtercimlap': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/blogter.png'),
		'url': 'http://cimlap.blogter.hu/index.php?action=suggest_link&title=TITLE&url=PERMALINK',
	},
	'Blue Dot': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/bluedot.png'),
		'url': 'http://bluedot.us/Authoring.aspx?>u=PERMALINK&title=TITLE',
	},
	'Book.mark.hu': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/bookmarkhu.png'),
		'url': 'http://book.mark.hu/bookmarks.php/?action=add&address=PERMALINK%2F&title=TITLE',
	},
	'Bumpzee': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/bumpzee.png'),
		'url': 'http://www.bumpzee.com/bump.php?u=PERMALINK',
	},
	'co.mments': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/co.mments.gif'),
		'url': 'http://co.mments.com/track?url=PERMALINK&title=TITLE',
	},
	'connotea': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/connotea.png'),
		'url': 'http://www.connotea.org/addpopup?continue=confirm&uri=PERMALINK&title=TITLE',
	},
	'del.icio.us': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/delicious.png'),
		'url': 'http://del.icio.us/post?url=PERMALINK&title=TITLE',
	},
	'De.lirio.us': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/delirious.png'),
		'url': 'http://de.lirio.us/rubric/post?uri=PERMALINK;title=TITLE;when_done=go_back',
	},
	'Digg': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/digg.png'),
		'url': 'http://digg.com/submit?phase=2&url=PERMALINK&title=TITLE',
		'description': 'bodytext',
	},
	'DotNetKicks': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/dotnetkicks.png'),
		'url': 'http://www.dotnetkicks.com/kick/?url=PERMALINK&title=TITLE',
		'description': 'description',
	},
	'DZone': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/dzone.png'),
		'url': 'http://www.dzone.com/links/add.html?url=PERMALINK&title=TITLE',
		'description': 'description',
	},
	'Fark': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/fark.png'),
		'url': 'http://cgi.fark.com/cgi/fark/edit.pl?new_url=PERMALINK&new_comment=TITLE&new_comment=BLOGNAME&linktype=Misc',
	},
	'feedmelinks': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/feedmelinks.png'),
		'url': 'http://feedmelinks.com/categorize?from=toolbar&op=submit&url=PERMALINK&name=TITLE',
	},
	'Furl': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/furl.png'),
		'url': 'http://www.furl.net/storeIt.jsp?u=PERMALINK&t=TITLE',
	},
	'Fleck': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/fleck.gif'),
		'url': 'http://extension.fleck.com/?v=b.0.804&url=PERMALINK',
	},
	'Gwar': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/gwar.gif'),
		'url': 'http://www.gwar.pl/DodajGwar.html?u=PERMALINK',
	},
	'Haohao': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/haohao.png'),
		'url': 'http://www.haohaoreport.com/submit.php?url=PERMALINK&title=TITLE',
	},
	'Hemidemi': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/hemidemi.png'),
		'url': 'http://www.hemidemi.com/user_bookmark/new?title=TITLE&url=PERMALINK',
	},
	'IndiaGram': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/indiagram.png'),
		'url': 'http://www.indiagram.com/mock/bookmarks/desitrain?action=add&address=PERMALINK&title=TITLE',
	},
	'IndianPad': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/indianpad.png'),
		'url': 'http://www.indianpad.com/submit.php?url=PERMALINK',
	},
	'Internetmedia': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/im.png'),
	},
	'kick.ie': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/kickit.png'),
		'url': 'http://kick.ie/submit/?url=PERMALINK&title=TITLE',
	},
	'LinkaGoGo': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/linkagogo.png'),
		'url': 'http://www.linkagogo.com/go/AddNoPopup?url=PERMALINK&title=TITLE',
	},
	'Linkter': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/linkter.png'),
		'url': 'http://www.linkter.hu/index.php?action=suggest_link&url=PERMALINK&title=TITLE',
	},
	'Ma.gnolia': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/magnolia.png'),
		'url': 'http://ma.gnolia.com/bookmarklet/add?url=PERMALINK&title=TITLE',
	},
	'MisterWong': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/misterwong.gif'),
		'url': 'http://www.mister-wong.com/addurl/?bm_url=PERMALINK&bm_description=TITLE&plugin=soc',
	},
	'MyShare': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/myshare.png'),
		'url': 'http://myshare.url.com.tw/index.php?func=newurl&url=PERMALINK&desc=TITLE',
	},
	'NewsVine': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/newsvine.png'),
		'url': 'http://www.newsvine.com/_tools/seed&save?u=PERMALINK&h=TITLE',
	},
	'Netscape': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/netscape.gif'),
		'url': 'http://www.netscape.com/submit/?U=PERMALINK&T=TITLE',
	},
	'Netvouz': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/netvouz.png'),
		'url': 'http://www.netvouz.com/action/submitBookmark?url=PERMALINK&title=TITLE&popup=no',
	},
	'PlugIM': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/plugim.png'),
		'url': 'http://www.plugim.com/submit?url=PERMALINK&title=TITLE',
	},
	'PopCurrent': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/popcurrent.png'),
		'url': 'http://popcurrent.com/submit?url=PERMALINK&title=TITLE&rss=RSS',
	},
	'ppnow': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/ppnow.png'),
		'url': 'http://www.ppnow.net/submit.php?url=PERMALINK',
	},
	'RawSugar': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/rawsugar.png'),
		'url': 'http://www.rawsugar.com/tagger/?turl=PERMALINK&tttl=TITLE',
	},
	'Rec6': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/rec6.gif'),
		'url': 'http://www.syxt.com.br/rec6/link.php?url=PERMALINK&=TITLE',
	},
	'Reddit': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/reddit.png'),
		'url': 'http://reddit.com/submit?url=PERMALINK&title=TITLE',
	},
	'Scoopeo': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/scoopeo.png'),
		'url': 'http://www.scoopeo.com/scoop/new?newurl=PERMALINK&title=TITLE',
	},
	'scuttle': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/scuttle.png'),
		'url': 'http://www.scuttle.org/bookmarks.php/maxpower?action=add&address=PERMALINK&title=TITLE',
	},
	'Shadows': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/shadows.png'),
		'url': 'http://www.shadows.com/features/tcr.htm?url=PERMALINK&title=TITLE',
	},
	'Simpy': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/simpy.png'),
		'url': 'http://www.simpy.com/simpy/LinkAdd.do?href=PERMALINK&title=TITLE&src=sociable-VERSION',
	},
	'Slashdot': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/slashdot.png'),
		'url': 'http://slashdot.org/bookmark.pl?title=TITLE&url=PERMALINK',
	},
	'Smarking': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/smarking.png'),
		'url': 'http://smarking.com/editbookmark/?url=PERMALINK&title=TITLE',
	},
	'Spurl': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/spurl.png'),
		'url': 'http://www.spurl.net/spurl.php?url=PERMALINK&title=TITLE',
	},
	'SphereIt': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/sphere.png'),
		'url': 'http://www.sphere.com/search?q=sphereit:PERMALINK&title=TITLE',
	},
	'StumbleUpon': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/stumbleupon.png'),
		'url': 'http://www.stumbleupon.com/url/PERMALINK',
	},
	'Taggly': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/taggly.png'),
		'url': 'http://taggly.com/bookmarks.php/pass?action=add&address=',
	},
	'Technorati': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/technorati.png'),
		'url': 'http://technorati.com/faves?add=PERMALINK',
	},
	'TailRank': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/tailrank.png'),
		'url': 'http://tailrank.com/share/?text=&link_href=PERMALINK&title=TITLE',
	},
	'ThisNext': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/thisnext.png'),
		'url': 'http://www.thisnext.com/pick/new/submit/sociable/?url=PERMALINK&name=TITLE',
	},
	'Webride': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/webride.png'),
		'url': 'http://webride.org/discuss/split.php?uri=PERMALINK&title=TITLE',
	},
	'Wists': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/wists.png'),
		'url': 'http://wists.com/s.php?c=&r=PERMALINK&title=TITLE',
		'class': 'wists',
	},
	'Wykop': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/wykop.gif'),
		'url': 'http://www.wykop.pl/dodaj?url=PERMALINK',
	},
	'YahooMyWeb': {
		'favicon': turbogears.url('/tg_widgets/tgsociable/images/yahoomyweb.png'),
		'url': 'http://myweb2.search.yahoo.com/myresults/bookmarklet?u=PERMALINK&=TITLE',
	},
}
