class Promisify{
    async request(options?:RequestOptions){
        let raw = await new Promise<RequestSuccessCallbackResult>((resolve, reject)=>{
            options["success"] = resolve;
            options["fail"] = reject;
            uni.request(options)
        });
        if(raw.statusCode >= 400){
            throw raw;
        }
        return raw
    }
}

const promisify: Promisify = new Promisify();
export default promisify