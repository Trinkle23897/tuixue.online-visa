export const checkVisaType = visaType => {
    return typeof visaType === "string" && "FBOHL".includes(visaType);
};

export const checkVisaTypeLst = visaTypeLst => visaTypeLst.every(vt => checkVisaType(vt));

export const checkEmbassyCode = embssyCode => {
    const embassyCodeLst = [
        "bj",
        "sh",
        "cd",
        "gz",
        "sy",
        "hk",
        "tp",
        "pp",
        "sg",
        "sel",
        "mel",
        "per",
        "syd",
        "brn",
        "fuk",
        "itm",
        "oka",
        "cts",
        "hnd",
        "ktm",
        "bkk",
        "cnx",
        "bfs",
        "lcy",
        "yyc",
        "yhz",
        "yul",
        "yow",
        "yqb",
        "yyz",
        "yvr",
        "auh",
        "dxb",
        "beg",
        "cdg",
        "gye",
        "uio",
        "esb",
        "ist",
        "ath",
        "bog",
        "bgi",
        "cjs",
        "gdl",
        "hmo",
        "cvj",
        "mid",
        "mex",
        "mty",
        "ols",
        "nld",
        "tij",
    ];
    return typeof embssyCode === "string" && embassyCodeLst.includes(embssyCode);
};

export const checkEmbassyCodeLst = embassyCodeLst => embassyCodeLst.every(ec => checkEmbassyCode(ec));

export const checkDateObj = dtObj => {
    // https://stackoverflow.com/a/643827/10529848
    return Object.prototype.toString.call(dtObj) === "[object Date]";
};
