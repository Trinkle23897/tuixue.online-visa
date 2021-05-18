export const checkVisaType = visaType => {
    return typeof visaType === "string" && "FJBOHL".includes(visaType);
};

export const checkVisaTypeLst = visaTypeLst => visaTypeLst.every(vt => checkVisaType(vt));

export const checkEmbassyCode = embssyCode => {
    return typeof embssyCode === "string";
};

export const checkEmbassyCodeLst = embassyCodeLst => embassyCodeLst.every(ec => checkEmbassyCode(ec));

export const checkDateObj = dtObj => {
    // https://stackoverflow.com/a/643827/10529848
    return Object.prototype.toString.call(dtObj) === "[object Date]";
};
