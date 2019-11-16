<template>
  <div>
    <view class="cu-card flex mecard">
      <div
        class="cu-avatar round xl mecardavatar"
        :style="'background-image:url(/static/' + gender + '.png);'"
      ></div>
      <div class="content mecardtext" style="">
        <div class="name">{{name}}</div>
        <div v-for="(item, idx) in education" :key="idx" :class="'cu-capsule round'">
          <span :class="'cu-tag bg-' + colorList[idx]">{{item.department}}</span>
          <span :class="'cu-tag line-' + colorList[idx]">{{item.type}}</span>
        </div>
      </div>
    </view>
    <div class="cu-card flex mycard2 cu-list grid">
      <div class="cu-item" key="1">
        <navigator url="/pages/me/myParticipate">我参与的</navigator>
      </div>
      <div class="cu-item" key="2">
        <navigator url="/pages/me/mySponsor">我发起的</navigator>
      </div>
      <div class="cu-item" key="3">
        <navigator url="/pages/me/history">历史记录</navigator>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  data() {
    const app = getApp();
    console.log(app);
    return {
      name: app.globalData.userInfo.name,
      globalData: app.globalData,
      gender: app.globalData.userInfo.gender || "male",
      education: app.globalData.userInfo.education,
      colorList: ["blue", "cyan", "olive"]
    };
  }
});
</script>

<style>
.mecard {
  padding-top: 20px;
  padding-bottom: 20px;
  background-color: #fff;
}

.mycard2 {
  background-color: #fff;
  margin-top: 10px;
}

.mecardavatar {
  vertical-align: middle;
  margin-left: 10%;
}

.mecardtext {
  vertical-align: middle;
  padding-left: 12px;
}

.me-info {
  height: 180px;
}

.name {
  font-size: 18px;
}

.tag {
  margin-left: 8px;
  vertical-align: middle;
}

.me-avatar {
  width: 70px;
  height: 70px;
  background-position: 0% 0%;
  background-size: 100% 100%;
  background-repeat: no-repeat;
}
.me-verified {
  background-color: #5e068c !important;
  color: #fff;
}
</style>
