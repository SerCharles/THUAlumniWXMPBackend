<template>
    <view>
    <view class="cu-bar bg-white">
<!--        <view class="action">-->
<!--            <text class="cuIcon-back text-gray"></text> 返回-->
<!--        </view>-->
        <view class="content text-bold">
            发起活动
        </view>
    </view>
    <form @submit="submitNewActivity">
        <view class="cu-form-group margin-top-sm">
            <view class="title">活动名称</view>
            <input name="name" />
        </view>
        <view class="cu-form-group margin-top-sm">
        <view class="title">活动类型</view>
        <picker mode="multiSelector" @change="MultiChange" @columnchange="MultiColumnChange" :value="multiIndex" :range="multiArray">
            <view class="picker">
                {{multiArray[0][multiIndex[0]]}}，{{multiArray[1][multiIndex[1]]}}，{{multiArray[2][multiIndex[2]]}}
            </view>
        </picker>
    </view>
        <view class="cu-form-group margin-top-sm">
            <view class="title">地点</view>
            <input name="space" />
        </view>
        <view class="cu-form-group margin-top">
            <view class="title">开始时间</view>
            <picker mode="date" :value="startDate" :start="today" :end="maxDate" @change="onStartDateChange" name="startDate">
                <view class="picker">
                    {{startDate}}
                </view>
            </picker>
            <picker mode="time" :value="startTime" start="00:00" end="23:59" @change="onStartTimeChange" name="startTime">
                <view class="picker">
                    {{startTime}}
                </view>
            </picker>
        </view>
        <view class="cu-form-group margin-top">
            <view class="title">结束时间</view>
            <picker mode="date" :value="endDate" :start="startDate" :end="maxDate" @change="onEndDateChange" name="endDate">
                <view class="picker">
                    {{endDate}}
                </view>
            </picker>
            <picker mode="time" :value="endTime" :start="minStartTime" end="23:59" @change="onEndTimeChange" name="endTime">
                <view class="picker">
                    {{endTime}}
                </view>
            </picker>
        </view>
        <view class="cu-form-group margin-top">
            <view class="title">最大人数</view>
            <input name="maxUser" />
        </view>
        <view style="display: flex;justify-content: center">
            <button form-type="submit" class="cu-btn bg-green">提交</button>
        </view>
    </form>
    </view>
</template>

<script lang="ts">
    import Vue from 'vue'
    import {Component} from 'vue-property-decorator'
    import dateFormat from 'dateformat'
    import promisify from '../../apps/Promisify'
    import delay from 'delay';
    @Component
    export default class newActivity extends Vue{
        name: "newActivity";
        get today(): string{
            return dateFormat(new Date(), "yyyy-mm-dd")
        }
        maxDate = "2020-12-31";
        startDate: string = "请选择";
        startTime: string = "请选择";
        endDate: string = "请选择";
        endTime: string = "请选择";
        typeMultiData: Array<{name: string, children: Array<{name: string, children?: any}>}> = [
            {
                name: "个人活动",
                children: [
                    {
                        name: "聚餐"
                    },
                    {
                        name: "唱歌"
                    },
                    {
                        name: "跑步"
                    }
                ]
            },
            {
                name:"班级活动",
                children: [
                    {
                        name: "聚餐"
                    },
                    {
                        name: "唱歌"
                    },
                    {
                        name: "跑步"
                    }
                ]
            }
        ];
        typeMultiIndex: Array<number> = [];
        typeMultiArray: Array<Array<string>>;
        typeMultiChange(e){
            this.typeMultiIndex = e.detail.value
        }
        typeMultiColumnChange(e){
            let data = {
                index: this.typeMultiIndex,
                array: this.typeMultiArray
            };
            let column = e.detail.column;
            data.index[column] = e.detail.value;
        }

        get minStartTime(): string{
            if(this.endDate <= this.startDate){
                return this.startTime
            }
            else return "00:00"
        }
        onStartDateChange(e){
            console.log("qwq");
            this.startDate = e.detail.value
        }
        onStartTimeChange(e){
            this.startTime = e.detail.value
        }
        onEndDateChange(e){
            this.endDate = e.detail.value
        }
        onEndTimeChange(e){
            this.endTime = e.detail.value
        }
        async submitNewActivity(e){
            console.log(e.detail.value);
            let formData = e.detail.value;
            let res = await promisify.request({
                url: getApp().globalData.baseUrl + `/createActivity`,
                method: "POST",
                dataType: "json",
                data: {
                    name: formData.name,
                    place: formData.place,
                    start: this.startDate + " " + this.startTime,
                    end: this.endDate + " " + this.endTime,
                    maxUser: formData.maxUser
                }
            });
            console.log(res.data);
            uni.showToast({title: "成功", icon: "none"});
            await delay(1000);
            uni.navigateTo({
                url: `../activityList/activityDetail/activityDetail?activityId=${res.data.id}`
            })
        }
    }
</script>

<style scoped>
</style>