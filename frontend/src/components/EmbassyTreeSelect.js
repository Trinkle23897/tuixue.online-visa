import React, { useMemo } from "react";
import PropTypes from "prop-types";
import { TreeSelect, Space, Radio, Divider } from "antd";
import { useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { makeEmbassyTreeSelector } from "../redux/selectors";
import { useScreenXS } from "../hooks";

export default function EmbassyTreeSelect({ sys, setSys, ...treeSelectProps }) {
    const { t } = useTranslation();
    const screenXS = useScreenXS();
    const embassyTreeSelector = useMemo(() => makeEmbassyTreeSelector(sys, t, false), [sys, t]);
    const embassyTreeOptions = useSelector(state => embassyTreeSelector(state));

    const searchEmbassy = (inputValue, treeNode) => treeNode.title.toLowerCase().includes(inputValue.toLowerCase());
    const renderDropdown = originalNode => (
        <div style={{ padding: 16 }}>
            <SysSelect />
            <Divider />
            {originalNode}
        </div>
    );
    const SysSelect = () => (
        <Space>
            <span>{t("filter.systemDesc")}</span>
            <Radio.Group onChange={e => setSys(e.target.value)} value={sys}>
                {["all", "ais", "cgi"].map(s => (
                    <Radio key={s} value={s}>
                        {t(s)}
                    </Radio>
                ))}
            </Radio.Group>
        </Space>
    );

    return (
        <TreeSelect
            {...treeSelectProps}
            dropdownRender={renderDropdown}
            treeData={embassyTreeOptions}
            filterTreeNode={searchEmbassy}
            showSearch={!screenXS}
            allowClear
            maxTagCount={screenXS ? 3 : 9999}
        />
    );
}
EmbassyTreeSelect.propTypes = {
    sys: PropTypes.string.isRequired,
    setSys: PropTypes.func.isRequired,
};
