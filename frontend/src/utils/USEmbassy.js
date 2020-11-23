const embassyAttributeLst = ["nameCn", "nameEn", "code", "sys", "region", "continent", "country", "tzInfo"];
const embassyAttributeIdx = Object.fromEntries(embassyAttributeLst.map((attr, idx) => [attr, idx]));

/**
 *
 * @param {str} attr one of `embassyAttributeLst`.
 * @param {str} code embassyCode
 * @param {Array} embassyLst List of embassy attribute array
 */
export const findEmbassyAttributeByCode = (attr, code, embassyLst) => {
    if (embassyAttributeLst.includes(attr)) {
        const embassy = embassyLst.find(emb => emb[embassyAttributeIdx.code] === code);
        if (embassy) {
            return embassy[embassyAttributeIdx[attr]];
        }
    }
};

export const findEmbassyAttributeByAnotherAttr = (targetAttr, inputAttrKey, inputAttrVal, embassyLst) => {
    if (embassyAttributeLst.includes(targetAttr) && embassyAttributeLst.includes(inputAttrKey)) {
        const embassy = embassyLst.find(emb => emb[embassyAttributeIdx[inputAttrKey]] === inputAttrVal);
        if (embassy) {
            return embassy[embassyAttributeIdx[targetAttr]];
        }
    }
};
