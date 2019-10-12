<template>
    <view>
        <view class="cu-bar search bg-white">
            <view class="search-form round">
                <text class="cuIcon-search"></text>
                <input @focus="InputFocus" @blur="InputBlur" :adjust-position="false" type="text" placeholder="搜索活动" confirm-type="search"></input>
            </view>
            <view class="action">
                <button class="cu-btn bg-green shadow-blur round" @click="search">搜索</button>
            </view>
        </view>
        <scroll-view scroll-y="true" >
            <view class="cu-list menu">
                <view class="cu-item arrow" style="display: block" v-for="activity in activities_toShow" @click="jumpToActivityDetail($event, activity)">
                    <view>
                        <text class="cuIcon-activity"></text>
                        <text class="text-black text-xl">{{activity.name}}</text>
                    </view>
                    <view style="display: flex;justify-content: space-between;">
                        <view class="basis-df">
                            <view class="text-grey text-xs">时间:{{activity.start}}-{{activity.end}}</view>
                            <view class="text-grey text-xs">地点:{{activity.place}}</view>
                        </view>
                        <view class="basis-xs">
                            <text class="text-lg text-green">{{activity.curUser}}</text>
                            <text class="text-lg text-black">/</text>
                            <text class="text-lg text-red">{{activity.maxUser}}</text>
                        </view>
                    </view>
                </view>
            </view>
        </scroll-view>
    </view>
</template>

<script lang="ts">
    import Vue from 'vue'
    import {Component} from 'vue-property-decorator'
    import promisify from "@/apps/Promisify";

    @Component
    export default class mainList extends Vue{
        name!: "mainList";
        activities_toShow: ActivitySchema[] = [];
        async updateAllActivity(){
            let res = await promisify.request({
                url: getApp().globalData.baseUrl + `/getAllActivity?openId=${getApp().globalData.openId}`,
                method: "GET",
                dataType: "json",
            });
            this.activities_toShow = res.data.activityList
        }
        search(){
            uni.showToast({title: "尚未支持", icon:"none"})
        }
        onLoad(){
            // this.activities_toShow = [
            //     {name: "aaa", place: "bbb"},
            //     {name: "aaa", place: "bbb"},
            //     {name: "aaa", place: "bbb"},
            //     {name: "aaa", place: "bbb"},
            //     {name: "aaa", place: "bbb"},
            //     {name: "aaa", place: "bbb"}
            // ]
            this.updateAllActivity();
        }
        jumpToActivityDetail(event, a: ActivitySchema){
            uni.navigateTo({
                url: `../activityDetail/activityDetail?activityId=${a.id}`
            })
        }
    }
</script>

<style scoped>

</style>