import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { HashLink as Link } from "react-router-hash-link";
import { Row, Col, Button, Layout, Menu, Typography, Popover } from "antd";
import { MenuOutlined } from "@ant-design/icons";
import "./TuixueHeader.less";

const { Header } = Layout;
const { Title, Text } = Typography;

const Logo = () => (
    <Col xs={{ span: 12 }} lg={{ span: 4, push: 1 }} className="logo">
        <img src="https://via.placeholder.com/40" alt="tuixue logo" />
        <Title>Tuixue</Title>
    </Col>
);

const NavMenu = ({ mode, theme }) => {
    return (
        <Menu theme={theme} mode={mode}>
            <Menu.Item>
                {/* <Link to="/" component={Typography.Link}> */}
                Visa Status
                {/* </Link> */}
            </Menu.Item>
            <Menu.Item>Item 1</Menu.Item>
        </Menu>
    );
};
NavMenu.propTypes = {
    mode: PropTypes.oneOf(["vertical", "horizontal", "inline"]),
    theme: PropTypes.oneOf(["dark", "light"]),
};

const NavMenuPopover = () => {
    const [menuPop, setMenuPop] = useState(false);

    return (
        <Popover
            content={<NavMenu mode="vertical" theme="light" />}
            trigger="click"
            placement="bottomRight"
            arrowPointAtCenter
        >
            <Button size="large" icon={<MenuOutlined />} ghost />
        </Popover>
    );
};

export default function Nav() {
    // const [menuExpand, setMenuExpand] = useState(window.innerWidth >= 768);
    // useEffect(() => {
    //     const onResize = () => setMenuExpand(window.innerWidth >= 768);
    //     window.addEventListener("resize", onResize);
    //     return () => {
    //         window.removeEventListener("resize", onResize);
    //     };
    // });

    return (
        <Header className="tuixue-header">
            <Row gutter={{ xs: 16, lg: 32 }}>
                <Logo />
                <Col xs={{ span: 0 }} lg={{ span: 6, push: 1 }}>
                    <NavMenu mode="horizontal" theme="dark" />
                </Col>
                <Col xs={{ span: 4, push: 8 }} lg={{ span: 0 }}>
                    <NavMenuPopover />
                </Col>
            </Row>
        </Header>
    );
}
