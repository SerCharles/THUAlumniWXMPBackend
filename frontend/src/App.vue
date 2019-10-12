<script lang="ts">
    import Vue from 'vue';
    export default Vue.extend({
        mpType: 'app',
        globalData:{
            baseUrl: "http://thaluapitest.starrah.cn",
            openId: ""
        },
        onLaunch() {
            console.log('App Launch')
        },
        onShow() {
            console.log('App Show')
        },
        onHide() {
            console.log('App Hide')
        }
    });
</script>

<style>
@import "colorui/main.css";
@import "colorui/icon.css";
</style>
