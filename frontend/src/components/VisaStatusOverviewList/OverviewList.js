import React, { useMemo } from "react";
import { List } from "antd";
import { useSelector } from "react-redux";
import { makeOverviewDetailSelector } from "../../redux/selectors";
import { OverviewContent, OverviewHeader } from "./OverviewContent";
import { overviewAttrProps } from "./overviewPropTypes";
import "./VisaStatusOverview.less";

export default function VisaStatusOverviewList({ visaType }) {
    const overviewSelector = useMemo(() => makeOverviewDetailSelector(visaType), [visaType]);
    const overviewData = useSelector(state => overviewSelector(state));

    return (
        <List
            itemLayout="vertical"
            dataSource={overviewData}
            header={<OverviewHeader />}
            renderItem={overview => (
                <List.Item key={overview.embassyCode}>
                    <OverviewContent overview={overview} />
                </List.Item>
            )}
        />
    );
}
VisaStatusOverviewList.propTypes = {
    visaType: overviewAttrProps.overview,
};
