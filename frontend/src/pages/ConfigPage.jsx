import React, { useEffect, useState } from 'react';
import { message } from 'antd';
import { getConfig, saveConfig, startCrawler } from '../api/index';
import ConfigForm from '../components/ConfigForm';

export default function ConfigPage() {
  const [config, setConfig] = useState({});
  useEffect(() => {
    getConfig().then(setConfig);
  }, []);
  const handleSave = (values) => {
    saveConfig(values).then(() => message.success('配置已保存'));
  };
  const handleStart = (values) => {
    startCrawler(values).then(() => message.success('爬虫已启动'));
  };
  return <ConfigForm initialValues={config} onSave={handleSave} onStart={handleStart} />;
} 