interface UserInfo {
    openId: string;
    name: string;
    education: Array<{
        type: string,
        start: number,
        department: string,
    }>
    flag: string
}