interface ActivitySchema{
    id: string,
    name: string,
    place: string,
    start: string, //yyyy-mm-dd hh:MM:ss
    end: string, //yyyy-mm-dd hh:MM:ss
    maxUser: number,
    curUser: number,
    creator: string,
    participant: [string]
}