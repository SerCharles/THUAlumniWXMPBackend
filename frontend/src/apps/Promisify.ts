class CorrectedRequestSuccessCallbackResult{
    data?: string | any | ArrayBuffer;
    statusCode?: number;
    header?: any;
    constructor(data, statusCode, header){
        this.data = data;
        this.statusCode = statusCode;
        this.header = header
    }
}

class Promisify{
    async request(options?:RequestOptions){
        if(options.url.indexOf("?") == -1){
            options.url = options.url + "?session=" + (getApp().globalData as GlobalData).session
        }else{
            options.url = options.url + "&session=" + (getApp().globalData as GlobalData).session
        }
        let raw = await new Promise<RequestSuccessCallbackResult>((resolve, reject)=>{
            options["success"] = resolve;
            options["fail"] = reject;
            uni.request(options)
        });
        let res = new CorrectedRequestSuccessCallbackResult(raw.data, raw.statusCode, raw.header)
        if(res.statusCode >= 400){
            if(res.data && typeof(res.data) === 'object' && res.data.errid && res.data.errid >= 500 && res.data.errid <= 599) {
                uni.showToast({
                    title: res.data.errmsg || "发生错误，请稍后重试",
                    icon: "none"
                });
            }
            throw res;
        }
        return res
    }
}

const promisify: Promisify = new Promisify();
export default promisify