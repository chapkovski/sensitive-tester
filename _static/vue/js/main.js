(function(t){function e(e){for(var o,a,l=e[0],s=e[1],u=e[2],d=0,f=[];d<l.length;d++)a=l[d],Object.prototype.hasOwnProperty.call(i,a)&&i[a]&&f.push(i[a][0]),i[a]=0;for(o in s)Object.prototype.hasOwnProperty.call(s,o)&&(t[o]=s[o]);c&&c(e);while(f.length)f.shift()();return r.push.apply(r,u||[]),n()}function n(){for(var t,e=0;e<r.length;e++){for(var n=r[e],o=!0,l=1;l<n.length;l++){var s=n[l];0!==i[s]&&(o=!1)}o&&(r.splice(e--,1),t=a(a.s=n[0]))}return t}var o={},i={main:0},r=[];function a(e){if(o[e])return o[e].exports;var n=o[e]={i:e,l:!1,exports:{}};return t[e].call(n.exports,n,n.exports,a),n.l=!0,n.exports}a.m=t,a.c=o,a.d=function(t,e,n){a.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},a.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},a.t=function(t,e){if(1&e&&(t=a(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(a.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var o in t)a.d(n,o,function(e){return t[e]}.bind(null,o));return n},a.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return a.d(e,"a",e),e},a.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},a.p="/static/vue/";var l=window["webpackJsonp"]=window["webpackJsonp"]||[],s=l.push.bind(l);l.push=e,l=l.slice();for(var u=0;u<l.length;u++)e(l[u]);var c=s;r.push([0,"chunk-vendors"]),n()})({0:function(t,e,n){t.exports=n("56d7")},"034f":function(t,e,n){"use strict";var o=n("85ec"),i=n.n(o);i.a},"56d7":function(t,e,n){"use strict";n.r(e);n("e260"),n("e6cf"),n("cca6"),n("a79d");var o=n("a026"),i=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("v-container",{staticClass:"justify-content-center d-flex  flex-column  text-center maincontainer",style:t.cont},[n("v-row",[n("v-col",[t.lead?n("h4",{style:{color:"black"}},[t._v(" "+t._s(t.lead)+" ")]):t._e()])],1),n("v-row",[n("v-col",[n("v-card-title",{staticClass:"d-flex justify-center text-center white--text text-center d-flex justify-content-center ",style:{background:t.fieldCol,"border-radius":"25px"}},[n("transition",{attrs:{name:"fade",mode:"out-in",appear:""},on:{"after-enter":t.afterEnter,"before-leave":t.beforeLeave}},[n("span",{key:t.body,staticClass:"bodytext white--text text-center",style:{"text-align":"center"}},[t._v(" "+t._s(t.body)+" ")])])],1)],1)],1),n("v-row",[n("v-col",{style:{visibility:t.block?"hidden":"visible"}},[n("v-btn-toggle",{staticClass:"d-flex justify-content-center",class:t.btnFunctionClass,attrs:{rounded:""},model:{value:t.value,callback:function(e){t.value=e},expression:"value"}},t._l(t.likert,(function(e){return n("v-btn",{key:e[0],style:t.individualBtnStyle,attrs:{rounded:""},on:{click:function(n){return t.answer(e[0])}}},[t._v(" "+t._s(e[1])+" ")])})),1)],1)],1),n("div",{attrs:{"data-app":""}},[n("attention-failed",{attrs:{dialog:t.attentionFailed,error:t.attentionError},on:{input:function(e){t.attentionFailed=!1}}})],1)],1)},r=[],a=(n("caad"),n("b0c0"),n("f58a")),l={components:{AttentionFailed:a["a"]},data:function(){return{attentionError:window.attentionError,attentionFailed:!1,lead:window.field_desc["lead"],trans:!0,block:!0,no_q_left:!1,too_many_failures:!1,body:"",label:null,qid:null,field:null,value:null,toggle_exclusive:void 0,likert:window.field_range,progressValue:0}},computed:{btnFunctionClass:function(){var t=this.likert.length,e=["xs","sm"],n=e.includes(this.$vuetify.breakpoint.name);return n&&t<10?{"flex-column":!0,"align-items-stretch":!0}:{}},cont:function(){var t=["xs","sm"],e=t.includes(this.$vuetify.breakpoint.name);return e?{}:{"max-width":"760px"}},individualBtnStyle:function(){var t=this.likert.length,e=["xs","sm"],n=e.includes(this.$vuetify.breakpoint.name);return n&&t<10?{"min-width":"inherit"}:{width:100/t+"%!important","min-width":"inherit"}},fieldCol:function(){var t={attitude:"black",average_attitude:"red",friend:"blue",absolute_importance:"#565656"};return t[this.field]||"black"}},watch:{progressValue:function(t){window.vueProgress.progressValue=t},no_q_left:function(t){t&&document.getElementById("form").submit()},too_many_failures:function(t){t&&document.getElementById("form").submit()}},mounted:function(){var t=this;this.$options.sockets.onmessage=function(e){var n=JSON.parse(e["data"]);t.trans=!1,t.attentionFailed=n.attention_failed,t.no_q_left=n.no_q_left,t.too_many_failures=n.too_many_failures,t.body=n.body,t.label=n.label,t.qid=n.id,t.field=n.field,t.value=n.value,t.progressValue=n.progress_value},this.trans=!0,this.$options.sockets.onopen=function(e){t.$socket.sendObj({info_request:!0})}},methods:{afterEnter:function(){this.block=!1},beforeLeave:function(){this.block=!0},answer:function(t){this.trans=!0,this.$socket.sendObj({answer:!0,qid:this.qid,field:this.field,value:t,body:this.body}),this.value=null}}},s=l,u=(n("034f"),n("2877")),c=n("6544"),d=n.n(c),f=n("8336"),v=n("a609"),p=n("99d9"),b=n("62ad"),h=n("a523"),m=n("0fd9"),y=Object(u["a"])(s,i,r,!1,null,null,null),_=y.exports;d()(y,{VBtn:f["a"],VBtnToggle:v["a"],VCardTitle:p["c"],VCol:b["a"],VContainer:h["a"],VRow:m["a"]});var w=n("b408"),g=n.n(w),x=(n("d1e78"),n("5363"),n("ce5b")),k=n.n(x),O=(n("bf40"),n("9955")),j=n.n(O),V=n("2ef0"),C=n.n(V);o["default"].use(j.a,{name:"custom",lodash:C.a}),o["default"].use(k.a),o["default"].config.productionTip=!1;var $="https:"===window.location.protocol?"wss":"ws",q=$+"://"+window.location.host+window.socket_path;o["default"].use(g.a,q,{format:"json",reconnection:!0,reconnectionAttempts:5,reconnectionDelay:3e3}),window.vueOpinion=new o["default"]({vuetify:new k.a({defaultAssets:{font:!0,icons:"mdi"},icons:{iconfont:"mdi"}}),render:function(t){return t(_)}}).$mount("#app")},"85ec":function(t,e,n){},f58a:function(t,e,n){"use strict";var o=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{staticClass:"text-center"},[n("v-dialog",{attrs:{value:t.dialog,width:"500"},on:{input:t.emitOutput}},[n("v-card",[n("v-card-title",{staticClass:"headline grey lighten-2"},[t._v(" "+t._s(t.error.title)+" ")]),n("v-card-text",[t._v(" "+t._s(t.error.body)+" ")]),n("v-divider"),n("v-card-actions",[n("v-spacer"),n("v-btn",{attrs:{color:"error",text:""},on:{click:t.emitOutput}},[t._v(" "+t._s(t.error.button)+" ")])],1)],1)],1)],1)},i=[],r={props:{dialog:{type:Boolean,default:!1},error:{type:Object,default:function(){}}},computed:{showDialog:function(){return this.dialog}},methods:{emitOutput:function(t){this.$emit("input",t)}}},a=r,l=n("2877"),s=n("6544"),u=n.n(s),c=n("8336"),d=n("b0af"),f=n("99d9"),v=n("169a"),p=n("ce7e"),b=n("2fa4"),h=Object(l["a"])(a,o,i,!1,null,null,null);e["a"]=h.exports;u()(h,{VBtn:c["a"],VCard:d["a"],VCardActions:f["a"],VCardText:f["b"],VCardTitle:f["c"],VDialog:v["a"],VDivider:p["a"],VSpacer:b["a"]})}});