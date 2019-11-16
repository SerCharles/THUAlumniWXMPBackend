import Vue from 'vue';
import initialGlobalData from './apps/typesDeclare/InitialGlobalData';
export default Vue.extend({
    globalData: initialGlobalData,
    mpType: 'app',
    onLaunch() {
        console.log('App Launch');
    },
    onShow() {
        console.log('App Show');
    },
    onHide() {
        console.log('App Hide');
    }
});
//# sourceMappingURL=App.vue.js.map