<template>
    <view>
    <view class="cu-bar bg-white">
        <view class="action" @click="back">
            <text class="cuIcon-back text-gray"></text> 返回
        </view>
        <view class="content text-bold">
            活动详情
        </view>
    </view>
    <view>
        <view>
            <text class="text-black text-bold text-sl">{{activityData.name}}</text>
        </view>
        <view>
            <text class="text-black text-bold text-sl">时间：{{activityData.start}}-{{activityData.end}}</text>
        </view>
        <view>
            <text class="text-black text-bold text-sl">地点：{{activityData.place}}</text>
        </view>
        <view>
            <text class="text-black text-bold text-sl">人数：{{activityData.curUser}}/{{activityData.maxUser}}</text>
        </view>
    </view>
    <view>
        <button class="cu-btn bg-green lg" @click="attendCurActivity">立即报名</button>
    </view>
    </view>
</template>

<script lang="ts">
    import Vue from 'vue'
    import {Component, Prop} from 'vue-property-decorator'
    import promisify from "@/apps/Promisify";

    @Component
    export default class activityDetail extends Vue{
        name!: "activityDetail";
        activityId: string = "";
        @Prop({type: Object, default: null})activityData: ActivitySchema = null;
        async updateActivityData(){
            if(!this.activityData){
                let res = await promisify.request({
                    url: getApp().globalData.baseUrl + `/getActivityInfo?openId=${getApp().globalData.openId}&activityId=${this.activityId}`,
                    method: "GET",
                    dataType: "json",
                });
                this.activityData = res.data
            }
        }
        async attendCurActivity(){
            let res = await promisify.request({
                url: getApp().globalData.baseUrl + `/joinActivity?openId=${getApp().globalData.openId}&activityId=${this.activityId}`,
                method: "POST",
                dataType: "json",
            });
            uni.showToast({
                title: res.data.result === "success"?"参加成功":"参加失败",
                icon: "none"
            })
        }
        onLoad(param: any){
            this.activityId = param.activityId;
            this.updateActivityData();
        }
        back(){
            uni.navigateBack();
        }
    }
</script>

<style scoped>

</style>