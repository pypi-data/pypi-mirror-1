/*
Copyright 2010 Isotoma Limited

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

$ = jQuery;

function get_cookies_array() {
    var cookies = { };
    if (document.cookie && document.cookie != '') {
        var split = document.cookie.split(';');
        for (var i = 0; i < split.length; i++) {
            var name_value = split[i].split("=");
            name_value[0] = name_value[0].replace(/^ /, '');
            if (name_value[0]=='__cp') {
            	// Zope copy support - trying to decode this throws malformedURI, skip over it
            	continue;
            }
            cookies[decodeURIComponent(name_value[0])] = decodeURIComponent(name_value[1]);
        }
    }
    return cookies;
}

/**
 * @param domain the i18n domain
 * @param msgs A list of objects containing the variables 'msgid' and 'default'
 * @param callback A function called with a translations object as the first argument, mapping msgids to translated values.
 *                 In the context of the callback, "this" is the window object.
 * @param language (optional) The two-letter language code as specified by ISO 639-1
 * @param reload (optional) If set to true, any cached values for these translations will be ignored,
 *                 and the values will be fetched by AJAX anew. 
 * @param debug (optional) If set to true, debugging messages will be written to the console.
 * @return void
 */
function translate(domain, msgs, callback, language, reload, debug) {
	if (language===undefined || language === null) {
		language = document.getElementsByTagName('html')[0].lang;
	}
	var url = 'translate.js?_jsl10n_domain='+escape(domain)+'&_jsl10n_lang='+escape(language);
	// indexed by jsl10n:language:domain:msg_id
	var cookies=get_cookies_array();
	var cookie_prefix='jsl10n:'+language+':'+domain+':';
	var cached_translations=[];
	var ajax_required=false;
	for (var i=0; i<msgs.length; i++) {
		var msg = msgs[i];
		if (!msg) continue;
		if (reload) {
			// kill any existing cookie:
			$.cookie(escape(cookie_prefix+msg['msgid']), null);
		}
		var translation=cookies[cookie_prefix+msg['msgid']];
		if (translation===undefined || translation===null || unescape(translation)=='') {
			if (debug) { console.log('requesting new msgid: "'+msg['msgid']+'" cached value ('+cookie_prefix+msg['msgid']+') is: "'+translation+'"'); }
			url+='&'+escape(msg['msgid'])+'='+escape(msg['default']);
			ajax_required=true;
		} else {
			translation=unescape(translation);
			cached_translations.push({'msgid':msg['msgid'],'translation':translation});
			if (debug) { console.log('using cached msgid: "'+msg['msgid']+': "'+translation+'"'); }
		}
	}
	if (ajax_required) {
		$.getJSON(url, function(data, textStatus) {
			if (textStatus!='success') {
				data = {};
			} else {
				$.each(data, function(msgid, msg) {
					if (msgid && data.hasOwnProperty(msgid) && typeof(msg)=='string') {
						// if we've got this far, the msgid was missing from our cache: add it.
						$.cookie(escape(cookie_prefix+msgid), escape(msg));
					}
				});
			}
			if (textStatus!='success') {
				if (debug) { console.log('JSON request failed, returning defaults without caching.'); }
				// if not successful, return the defaults but do not cache.
				for (var i=0; i<msgs.length; i++) {
					data[msgs[i].msgid] = msgs[i]['default'];
				}
			}
			for (var i=0;i<cached_translations.length;i++) {
				data[cached_translations[i]['msgid']]=cached_translations[i]['translation'];
			}
			callback(data);
		});
	} else {
		var data = {};
		for (var j=0;j<cached_translations.length;j++) {
			data[cached_translations[j]['msgid']]=cached_translations[j]['translation'];
		}
		callback(data);
	}
}
