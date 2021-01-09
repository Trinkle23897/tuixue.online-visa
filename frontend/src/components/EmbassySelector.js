import React, { useMemo, useState, useEffect } from "react";
import PropTypes from "prop-types";
import { Card, Space, Button, Row, Col } from "antd";
import { useSelector, useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { updateFilterAndFetch } from "../redux/visastatusFilterSlice";
import { makeFilterSelectorByVisaType, makeEmbassyBySysSelector } from "../redux/selectors";
import EmbassyTreeSelect from "./EmbassyTreeSelect";

export default function EmbassySelector({ visaType }) {
    const [t] = useTranslation();
    const [sys, setSys] = useState("all");

    const embassyBySysSelector = useMemo(() => makeEmbassyBySysSelector(sys), [sys]);
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

    const SelectDefaultFilter = () => <Button onClick={() => resetFilter()}>{t("filter.default")}</Button>;
    const SelectDomesticOnly = () => (
        <Button
            onClick={() => domesticRegion && dispatch(updateFilterAndFetch(visaType, domesticRegion.embassyCodeLst))}
        >
            {t("filter.domestic")}
        </Button>
    );

    return (
        <Card
            title={
                <Row justify="space-between">
                    <Col xs={{ span: 24 }} md={{ span: 10 }}>
                        {t("filter.desc")}
                    </Col>
                    <Col>
                        <Space>
                            <SelectDefaultFilter />
                            <SelectDomesticOnly />
                        </Space>
                    </Col>
                </Row>
            }
        >
            <EmbassyTreeSelect
                sys={sys}
                setSys={s => setSys(s)}
                value={displayValue}
                onChange={value => dispatch(updateFilterAndFetch(visaType, value))}
                onDropdownVisibleChange={open => setDropdownOpen(open)}
                treeDefaultExpandedKeys={["DOMESTIC"]}
                placeholder="Search or select U.S. Embassy or Consulate"
                style={{ width: "100%" }}
                size="large"
                multiple
                treeCheckable
            />
        </Card>
    );
}
EmbassySelector.propTypes = {
    visaType: PropTypes.string.isRequired,
};
