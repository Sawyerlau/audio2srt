import React from 'react';
import { Layout, Card, Form, Input, Button, message } from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { useConfigStore } from '../stores/useConfigStore';

const { Content } = Layout;

const Settings: React.FC = () => {
  const { config, setConfig, saveConfig } = useConfigStore();
  const [form] = Form.useForm();

  const handleSave = async (values: any) => {
    setConfig(values);
    await saveConfig();
    message.success('配置保存成功！');
  };

  return (
    <div style={{ padding: '24px', overflowX: 'hidden' }}>
      <Card title="系统设置">
        <Form
          form={form}
          layout="vertical"
          initialValues={config}
          onFinish={handleSave}
        >
          <Form.Item
            name="API_KEY"
            label="API Key"
            rules={[{ required: true, message: '请输入API Key' }]}
          >
            <Input.Password
              placeholder="请输入火山引擎API Key"
            />
          </Form.Item>

          <Form.Item
            name="RESOURCE_ID"
            label="Resource ID"
            rules={[{ required: true, message: '请输入Resource ID' }]}
          >
            <Input
              placeholder="volc.bigasr.auc"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              size="large"
            >
              保存配置
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <Card title="获取API Key" style={{ marginTop: '24px' }}>
        <ol>
          <li>登录火山引擎控制台</li>
          <li>进入豆包语音产品页面</li>
          <li>获取API Key并填入上方</li>
        </ol>
      </Card>
    </div>
  );
};

export default Settings;
