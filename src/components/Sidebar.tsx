import React from 'react';
import { Layout, Menu } from 'antd';
import {
  AudioOutlined,
  FileTextOutlined,
  SettingOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';

const { Sider } = Layout;

interface SidebarProps {
  activeKey: string;
  onMenuClick: (key: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeKey, onMenuClick }) => {
  const menuItems = [
    {
      key: 'audio',
      icon: <AudioOutlined />,
      label: '音频转SRT'
    },
    {
      key: 'srt',
      icon: <FileTextOutlined />,
      label: 'SRT优化'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置'
    },
    {
      key: 'help',
      icon: <QuestionCircleOutlined />,
      label: '帮助中心'
    }
  ];

  return (
    <Sider width={200} theme="light">
      <div style={{ padding: '16px', textAlign: 'center' }}>
        <h2 style={{ margin: 0, fontSize: '18px' }}>字幕工具箱</h2>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[activeKey]}
        items={menuItems}
        onClick={({ key }) => onMenuClick(key)}
      />
    </Sider>
  );
};

export default Sidebar;
