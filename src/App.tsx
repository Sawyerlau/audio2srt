import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import AudioToSRT from './components/AudioToSRT';
import SrtOptimizer from './components/SrtOptimizer';
import Settings from './components/Settings';
import HelpCenter from './components/HelpCenter';
import { useConfigStore } from './stores/useConfigStore';

const App: React.FC = () => {
  const [activeKey, setActiveKey] = useState('audio');
  const { loadConfig } = useConfigStore();

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  const handleMenuClick = (key: string) => {
    console.log('切换到页面:', key);
    setActiveKey(key);
  };

  const renderContent = () => {
    console.log('当前渲染页面:', activeKey);
    switch (activeKey) {
      case 'audio':
        return <AudioToSRT />;
      case 'srt':
        return <SrtOptimizer />;
      case 'settings':
        return <Settings />;
      case 'help':
        return <HelpCenter />;
      default:
        return <AudioToSRT />;
    }
  };

  return (
    <div style={{ 
      position: 'relative', 
      height: '100vh', 
      width: '100vw', 
      overflow: 'hidden',
      margin: 0,
      padding: 0,
      background: '#f0f2f5'
    }}>
      {/* 左侧固定 */}
      <div style={{ 
        position: 'fixed', 
        left: 0, 
        top: 0, 
        bottom: 0, 
        width: 200,
        zIndex: 10,
        background: '#fff',
        boxShadow: '2px 0 8px rgba(0,0,0,0.1)'
      }}>
        <Sidebar activeKey={activeKey} onMenuClick={handleMenuClick} />
      </div>
      {/* 右侧可滚动（只在这里设置滚动条） */}
      <div style={{ 
        position: 'fixed',
        left: 200,
        top: 0,
        right: 0,
        bottom: 0,
        overflowY: 'auto',
        overflowX: 'hidden',
        background: '#f0f2f5'
      }}>
        {renderContent()}
      </div>
    </div>
  );
};

export default App;
