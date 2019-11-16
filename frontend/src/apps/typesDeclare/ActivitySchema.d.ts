interface ActivitySchema{
    id: string,
    name: string,
    place: string,
    start: string, //yyyy-mm-dd hh:MM:ss
    end: string, //yyyy-mm-dd hh:MM:ss
    minUser?: number
    maxUser?: number,
    curUser: number,
    creator: string,
    signupBeginAt: string,
    signupStopAt: string, //yyyy-mm-dd hh:MM:ss
    participants: [string]
    type: string,
    status: ActivityStatus
}

declare enum ActivityStatus {
    Except = 0, //异常情况（如活动被管理员禁止等）
    BeforeSignup = 1, //报名尚未开始
    Signup = 2, //报名中
    SignupPaused = 3, //报名被暂停（发起人主动）
    SignupStopped = 4, //报名已截止（到达设定的时间）
    Signin = 5, //签到中
    SigninPaused = 6, //签到被暂停
    Finish = 7, //活动已结束（到达设定的活动结束时间）
}