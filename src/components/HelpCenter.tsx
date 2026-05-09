import React, { useState } from 'react';
import { Layout, Card, Collapse } from 'antd';
import { HelpSection } from '../types';

const { Content } = Layout;
const { Panel } = Collapse;

const HelpCenter: React.FC = () => {
  const helpSections: HelpSection[] = [
    {
      title: '🚀 快速入门',
      content: `1. 点击左侧"音频转SRT"
2. 选择"本地文件"或"外链模式"
3. 添加音频文件或输入URL
4. 点击"开始处理"
5. 等待处理完成`,
      expanded: true
    },
    {
      title: '📝 音频转SRT',
      content: `支持两种模式：
- 本地文件模式：支持 MP3/WAV/M4A/FLAC/AAC/OGG 音频，以及 MP4/MKV/AVI/MOV/WMV/FLV/WEBM/M4V 视频
- 外链模式：每行一个 HTTP/HTTPS 音频链接

视频文件会自动提取音频为同名 MP3 文件。

支持批量处理，处理后会生成：
- filename.srt（原始字幕）
- filename_opt.srt（优化后字幕）
字幕文件与原文件同名`
    },
    {
      title: '✨ SRT优化',
      content: `优化功能：
- 自动按标点符号断句
- 控制每行字幕长度（默认25字符）
- 自动分配时间轴
- 自动删除句号

使用方法：
1. 点击左侧"SRT优化"
2. 选择已有的 SRT 字幕文件
3. 点击"开始优化"
4. 生成 filename_opt.srt`
    },
    {
      title: '⚙️ 设置说明',
      content: `配置项说明：
- API Key：火山引擎豆包语音 API 访问密钥
- Resource ID：使用的资源 ID（默认是录音文件识别 1.0）

获取方式：
1. 登录火山引擎控制台
2. 在管理页面获取 API Key 并填入设置中

更多信息请访问火山引擎文档`
    },
    {
      title: '❓ 常见问题',
      content: `Q: 处理速度慢怎么办？
A: 取决于网络状况和音频长度，请耐心等待

Q: 支持什么音频格式？
A: 本地支持 MP3/WAV/M4A/FLAC/AAC/OGG，外链支持主流格式

Q: 配置文件在哪里？
A: 配置存储在用户目录下，会自动加载`
    }
  ];

  return (
    <div style={{ padding: '24px', overflowX: 'hidden' }}>
      <Card title="帮助中心">
        <Collapse defaultActiveKey={helpSections.map((_, index) => index.toString())}>
          {helpSections.map((section, index) => (
            <Panel header={section.title} key={index.toString()}>
              <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                {section.content}
              </pre>
            </Panel>
          ))}
        </Collapse>
      </Card>
    </div>
  );
};

export default HelpCenter;
