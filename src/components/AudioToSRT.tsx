import React, { useEffect } from 'react';
import {
  Card,
  Tabs,
  Button,
  List,
  Typography,
  Progress,
  Space,
  Input,
  message
} from 'antd';
import {
  UploadOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { useAudioStore } from '../stores/useAudioStore';
import { useConfigStore } from '../stores/useConfigStore';

const { TextArea } = Input;
const { Text } = Typography;

const AudioToSRT: React.FC = () => {
  const {
    mode,
    files,
    urls,
    logs,
    progress,
    isProcessing,
    setMode,
    addFiles,
    removeFile,
    clearFiles,
    setUrls,
    addLog,
    clearLogs,
    setProgress,
    setIsProcessing
  } = useAudioStore();

  const { config } = useConfigStore();

  useEffect(() => {
    if (!window.electronAPI?.python?.onLog) return;
    const cleanup = window.electronAPI.python.onLog((log) => {
      addLog(log);
    });
    return cleanup;
  }, []);

  const handleZoneClick = () => {
    handleSelectFiles();
  };

  const handleSelectFiles = async () => {
    try {
      if (!window.electronAPI?.dialog?.openFiles) {
        message.warning('请在 Electron 环境中使用');
        return;
      }
      const selectedFiles = await window.electronAPI.dialog.openFiles();
      if (selectedFiles && selectedFiles.length > 0) {
        addFiles(selectedFiles);
      }
    } catch (error) {
      console.error('选择文件失败:', error);
      message.error('选择文件失败');
    }
  };

  const handleStart = async () => {
    if (!config.API_KEY) {
      message.warning('请先在设置中配置API Key');
      return;
    }

    if (mode === 'local' && files.length === 0) {
      message.warning('请先选择文件');
      return;
    }

    if (mode === 'url' && !urls.trim()) {
      message.warning('请先输入URL');
      return;
    }

    if (!window.electronAPI?.python?.processAudio) {
      message.warning('请在 Electron 环境中使用');
      return;
    }

    setIsProcessing(true);
    clearLogs();
    setProgress(0);

    try {
      const inputs = mode === 'local'
        ? files.map(f => f.path)
        : urls.split('\n').filter(u => u.trim().startsWith('http'));

      const result = await window.electronAPI.python.processAudio({
        type: mode,
        inputs,
        config
      });

      setProgress(100);

      if (result.success) {
        message.success('处理完成！');
      } else {
        message.error('处理失败');
      }
    } catch (error) {
      console.error('处理出错:', error);
      message.error('处理出错');
      addLog(`错误: ${error}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const tabItems = [
    {
      key: 'local',
      label: '本地文件',
      children: (
        <div>
          <div
            onClick={handleZoneClick}
            style={{
              border: '2px dashed #d9d9d9',
              borderRadius: '8px',
              padding: '40px',
              textAlign: 'center',
              cursor: 'pointer',
              marginBottom: '16px',
              transition: 'all 0.3s'
            }}
          >
            <UploadOutlined
              style={{
                fontSize: '48px',
                color: '#d9d9d9',
                marginBottom: '16px'
              }}
            />
            <p>点击选择文件（支持多选）</p>
          </div>

          <Space style={{ marginBottom: '16px' }}>
            <Button
              icon={<ClearOutlined />}
              onClick={clearFiles}
              disabled={isProcessing}
              danger
            >
              清空
            </Button>
          </Space>

          <List
            dataSource={files}
            renderItem={(file) => (
              <List.Item
                actions={[
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => removeFile(file.id)}
                    disabled={isProcessing}
                  />
                ]}
              >
                <List.Item.Meta
                  title={file.name}
                  description={file.type === 'video' ? '视频文件' : '音频文件'}
                />
              </List.Item>
            )}
            locale={{ emptyText: '暂无文件' }}
          />
        </div>
      )
    },
    {
      key: 'url',
      label: '外链模式',
      children: (
        <div>
          <TextArea
            rows={8}
            placeholder="请输入音频URL，每行一个"
            value={urls}
            onChange={(e) => setUrls(e.target.value)}
            disabled={isProcessing}
          />
        </div>
      )
    }
  ];

  return (
    <div style={{ padding: '24px', overflowX: 'hidden' }}>
      <Card title="批量音频转SRT" style={{ marginBottom: '24px' }}>
        <Tabs
          activeKey={mode}
          onChange={(key) => setMode(key as 'local' | 'url')}
          items={tabItems}
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
          onClick={handleStart}
          disabled={isProcessing}
          style={{ width: '200px' }}
        >
          {isProcessing ? '处理中...' : '开始处理'}
        </Button>
      </div>
    </div>
  );
};

export default AudioToSRT;
