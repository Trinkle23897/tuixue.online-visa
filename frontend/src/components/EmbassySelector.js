import React, { useMemo, useState, useEffect } from "react";
import PropTypes from "prop-types";
import { Card, Divider, Radio, Space, TreeSelect, Button, Row, Col } from "antd";
import { useSelector, useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { updateFilterAndFetch } from "../redux/visastatusFilterSlice";
import { makeFilterSelectorByVisaType, makeEmbassyTreeSelector, makeEmbassyBySysSelector } from "../redux/selectors";

export default function EmbassySelector({ visaType }) {
    const [t] = useTranslation();
    const [sys, setSys] = useState("all");
    const embassyTreeSelector = useMemo(() => makeEmbassyTreeSelector(sys, t), [sys, t]);
    const embassyBySysSelector = useMemo(() => makeEmbassyBySysSelector(sys), [sys]);
    const embassyTreeOptions = useSelector(state => embassyTreeSelector(state));
    const embassyBySys = useSelector(state => embassyBySysSelector(state));

    const filterSelector = useMemo(() => makeFilterSelectorByVisaType(visaType), [visaType]);
    const vsFilter = useSelector(state => filterSelector(state));
    const defaultFilter = useSelector(state => state.metadata.defaultFilter);
    const displayValue = useMemo(() => vsFilter.filter(code => embassyBySys.includes(code)), [vsFilter, embassyBySys]);

    const domesticRegion = useSelector(state => state.metadata.region.find(r => r.region === "DOMESTIC"));
    const dispatch = useDispatch();

    const [dropdownOpen, setDropdownOpen] = useState(null);
    useEffect(() => {
        if (dropdownOpen !== null && !dropdownOpen && JSON.stringify(displayValue) !== JSON.stringify(vsFilter)) {
            dispatch(updateFilterAndFetch(visaType, displayValue));
        }
    }, [visaType, dispatch, dropdownOpen, displayValue, vsFilter]);

    const resetFilter = () => (setSys("all") || true) && dispatch(updateFilterAndFetch(visaType, defaultFilter));
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
            <span>{t("filterSystemDesc")}</span>
            <Radio.Group onChange={e => setSys(e.target.value)} value={sys}>
                {["all", "ais", "cgi"].map(s => (
                    <Radio key={s} value={s}>
                        {t(s)}
                    </Radio>
                ))}
            </Radio.Group>
        </Space>
    );
    const SelectDefaultFilter = () => (
        <Button type="primary" onClick={() => resetFilter()}>
            {t("filterDefault")}
        </Button>
    );
    const SelectDomesticOnly = () => (
        <Button
            type="primary"
            onClick={() => domesticRegion && dispatch(updateFilterAndFetch(visaType, domesticRegion.embassyCodeLst))}
        >
            {t("filterDomestic")}
        </Button>
    );

    const SelectOverviewType = () => {
        return (
            <Button type="primary" onClick={console.log("switch from word to chart or chart to word")}>
                {t("filterOverviewType")}
            </Button>
        );
    };

    return (
        <Card
            title={
                <Row justify="space-between">
                    <Col span={10}>{t("filterDesc")}</Col>
                    <Space direction="horizontal">
                        <Col span={3}>
                            <SelectDefaultFilter />
                        </Col>
                        <Col span={3}>
                            <SelectDomesticOnly />
                        </Col>
                        <Col span={3}>
                            <SelectOverviewType />
                        </Col>
                    </Space>
                </Row>
            }
        >
            <TreeSelect
                dropdownRender={renderDropdown}
                treeData={embassyTreeOptions}
                value={displayValue}
                onChange={value => dispatch(updateFilterAndFetch(visaType, value))}
                onDropdownVisibleChange={open => setDropdownOpen(open)}
                filterTreeNode={searchEmbassy}
                treeDefaultExpandedKeys={["DOMESTIC"]}
                placeholder="Search or select U.S. Embassy or Consulate"
                style={{ width: "100%" }}
                size="large"
                showSearch
                multiple
                allowClear
                treeCheckable
            />
        </Card>
    );
}
EmbassySelector.propTypes = {
    visaType: PropTypes.string.isRequired,
};
