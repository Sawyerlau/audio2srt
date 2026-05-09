import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Progress, message, Typography } from 'antd';
import { FolderOpenOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useConfigStore } from '../stores/useConfigStore';

const { Text } = Typography;

const SrtOptimizer: React.FC = () => {
  const [filePath, setFilePath] = useState('');
  const [logs, setLogs] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const { config } = useConfigStore();

  useEffect(() => {
    if (!window.electronAPI?.python?.onLog) return;
    const cleanup = window.electronAPI.python.onLog((log) => {
      setLogs((prev) => [...prev, log]);
    });
    return cleanup;
  }, []);  // 空数组！只注册一次！

  const handleSelectFile = async () => {
    try {
      if (!window.electronAPI?.dialog?.openFile) {
        message.warning('请在 Electron 环境中使用');
        return;
      }
      const path = await window.electronAPI.dialog.openFile();
      if (path) {
        setFilePath(path);
      }
    } catch (error) {
      message.error('选择文件失败');
    }
  };

  const handleOptimize = async () => {
    if (!config.API_KEY) {
      message.warning('请先在设置中配置API Key');
      return;
    }

    if (!filePath) {
      message.warning('请先选择SRT文件');
      return;
    }

    if (!window.electronAPI?.python?.optimizeSrt) {
      message.warning('请在 Electron 环境中使用');
      return;
    }

    setIsProcessing(true);
    setLogs([]);
    setProgress(0);

    try {
      const result = await window.electronAPI.python.optimizeSrt({
        input_path: filePath,
        config
      });

      setProgress(100);

      if (result.success) {
        message.success('优化完成！');
      } else {
        message.error('优化失败');
      }
    } catch (error) {
      message.error('优化出错');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ padding: '24px', overflowX: 'hidden' }}>
      <Card title="SRT优化" style={{ marginBottom: '24px' }}>
        <Input.Search
          placeholder="选择SRT文件"
          value={filePath}
          readOnly
          enterButton={<Button icon={<FolderOpenOutlined />}>浏览</Button>}
          onSearch={handleSelectFile}
          style={{ marginBottom: '16px' }}
          disabled={isProcessing}
        />
      </Card>

      <Card title="处理日志" style={{ marginBottom: '24px' }}>
        <div
          style={{
            maxHeight: '300px',
            overflowY: 'auto',
            background: '#f5f5f5',
            padding: '12px',
            borderRadius: '4px',
            fontFamily: 'monospace'
          }}
        >
          {logs.length === 0 ? (
            <Text type="secondary">暂无日志</Text>
          ) : (
            logs.map((log, index) => (
              <div key={index} style={{ marginBottom: '4px' }}>{log}</div>
            ))
          )}
        </div>
      </Card>

      <div style={{ textAlign: 'center' }}>
        {isProcessing && (
          <div style={{ marginBottom: '16px' }}>
            <Progress percent={progress} status="active" />
          </div>
        )}
        <Button
          type="primary"
          size="large"
          icon={<PlayCircleOutlined />}
          onClick={handleOptimize}
          disabled={isProcessing}
          style={{ width: '200px' }}
        >
          {isProcessing ? '优化中...' : '开始优化'}
        </Button>
      </div>
    </div>
  );
};

export default SrtOptimizer;
