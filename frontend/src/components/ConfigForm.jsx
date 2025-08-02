import React, { useState } from 'react';
import { Form, Input, Select, Switch, Button, Collapse, Tooltip } from 'antd';

export default function ConfigForm({ initialValues, onSave, onStart }) {
  const [form] = Form.useForm();
  const [showAdvanced, setShowAdvanced] = useState(false);
  React.useEffect(() => {
    form.setFieldsValue(initialValues);
  }, [initialValues, form]);
  return (
    <Form form={form} layout="vertical" onFinish={onSave}>
      {/* 基础参数 */}
      <Form.Item name="platform" label="平台" rules={[{required:true}]}> 
        <Select options={[
          {value:'xhs',label:'小红书'},{value:'dy',label:'抖音'},{value:'ks',label:'快手'},
          {value:'bili',label:'B站'},{value:'wb',label:'微博'},{value:'tieba',label:'贴吧'},{value:'zhihu',label:'知乎'}
        ]}/>
      </Form.Item>
      <Form.Item name="keywords" label="关键词"><Input /></Form.Item>
      <Form.Item name="login_type" label="登录方式" rules={[{required:true}]}> 
        <Select options={[{value:'qrcode',label:'扫码'},{value:'phone',label:'手机号'},{value:'cookie',label:'Cookie'}]}/>
      </Form.Item>
      <Form.Item name="cookies" label="Cookies"><Input /></Form.Item>
      <Form.Item name="sort_type" label="排序类型"><Input /></Form.Item>
      <Form.Item name="publish_time_type" label="发布时间类型"><Input type="number" /></Form.Item>
      <Form.Item name="crawler_type" label="爬虫类型" rules={[{required:true}]}> 
        <Select options={[{value:'search',label:'搜索'},{value:'detail',label:'详情'},{value:'creator',label:'创作者'}]}/>
      </Form.Item>
      <Form.Item name="weibo_search_type" label="微博搜索类型"><Input /></Form.Item>
      <Form.Item name="ua" label="User Agent"><Input /></Form.Item>
      <Form.Item name="enable_ip_proxy" label="启用IP代理" valuePropName="checked"><Switch /></Form.Item>
      <Form.Item name="crawler_max_sleep_sec" label="最大爬取间隔(秒)"><Input type="number" /></Form.Item>
      <Form.Item name="ip_proxy_pool_count" label="代理池数量"><Input type="number" /></Form.Item>
      <Form.Item name="ip_proxy_provider_name" label="代理提供商"><Input /></Form.Item>
      <Form.Item name="headless" label="无头模式" valuePropName="checked"><Switch /></Form.Item>
      <Form.Item name="save_login_state" label="保存登录状态" valuePropName="checked"><Switch /></Form.Item>
      <Form.Item name="enable_cdp_mode" label="启用CDP模式" valuePropName="checked"><Switch /></Form.Item>
      <Form.Item name="cdp_debug_port" label="CDP端口"><Input type="number" /></Form.Item>
      <Form.Item name="custom_browser_path" label="自定义浏览器路径"><Input /></Form.Item>
      <Form.Item name="cdp_headless" label="CDP无头模式" valuePropName="checked"><Switch /></Form.Item>
      <Form.Item name="browser_launch_timeout" label="浏览器启动超时(秒)"><Input type="number" /></Form.Item>
      <Form.Item name="auto_close_browser" label="自动关闭浏览器" valuePropName="checked"><Switch /></Form.Item>
      <Form.Item name="save_data_option" label="数据保存方式"> 
        <Select options={[{value:'csv',label:'CSV'},{value:'db',label:'数据库'},{value:'json',label:'JSON'}]}/>
      </Form.Item>
      <Form.Item name="user_data_dir" label="用户数据目录"><Input /></Form.Item>
      <Form.Item name="start_page" label="起始页码"><Input type="number" /></Form.Item>
      <Form.Item name="crawler_max_notes_count" label="最大帖子数"><Input type="number" /></Form.Item>
      <Form.Item name="max_concurrency_num" label="最大并发数"><Input type="number" /></Form.Item>
      <Form.Item name="enable_get_images" label="爬取图片" valuePropName="checked"><Switch /></Form.Item>
      <Form.Item name="enable_get_comments" label="爬取一级评论" valuePropName="checked"><Switch /></Form.Item>
      <Form.Item name="crawler_max_comments_count_singlenotes" label="单帖最大评论数"><Input type="number" /></Form.Item>
      <Form.Item name="enable_get_sub_comments" label="爬取二级评论" valuePropName="checked"><Switch /></Form.Item>
      {/* 高级参数折叠区 */}
      <Collapse style={{marginBottom:16}} onChange={v=>setShowAdvanced(!!v.length)}>
        <Collapse.Panel header="高级设置（平台ID/URL/词云/时间等）" key="1">
          <Form.Item name="xhs_specified_note_url_list" label="小红书笔记URL列表"><Input.TextArea rows={2} placeholder="每行一个URL" /></Form.Item>
          <Form.Item name="dy_specified_id_list" label="抖音ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="ks_specified_id_list" label="快手ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="bili_specified_id_list" label="B站bvid列表"><Input.TextArea rows={2} placeholder="每行一个bvid" /></Form.Item>
          <Form.Item name="weibo_specified_id_list" label="微博帖子ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="weibo_creator_id_list" label="微博创作者ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="tieba_specified_id_list" label="贴吧帖子ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="tieba_name_list" label="贴吧名称列表"><Input.TextArea rows={2} placeholder="每行一个贴吧名" /></Form.Item>
          <Form.Item name="tieba_creator_url_list" label="贴吧创作者URL列表"><Input.TextArea rows={2} placeholder="每行一个URL" /></Form.Item>
          <Form.Item name="xhs_creator_id_list" label="小红书创作者ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="dy_creator_id_list" label="抖音创作者ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="bili_creator_id_list" label="B站创作者ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="ks_creator_id_list" label="快手创作者ID列表"><Input.TextArea rows={2} placeholder="每行一个ID" /></Form.Item>
          <Form.Item name="zhihu_creator_url_list" label="知乎创作者主页URL列表"><Input.TextArea rows={2} placeholder="每行一个URL" /></Form.Item>
          <Form.Item name="zhihu_specified_id_list" label="知乎帖子ID/URL列表"><Input.TextArea rows={2} placeholder="每行一个URL" /></Form.Item>
          <Form.Item name="enable_get_wordcloud" label="生成词云" valuePropName="checked"><Switch /></Form.Item>
          <Form.Item name="custom_words" label="自定义词组"><Input.TextArea rows={2} placeholder="格式：词:分组，每行一个" /></Form.Item>
          <Form.Item name="stop_words_file" label="停用词文件路径"><Input /></Form.Item>
          <Form.Item name="font_path" label="字体文件路径"><Input /></Form.Item>
          <Form.Item name="start_day" label="B站爬取起始日"><Input /></Form.Item>
          <Form.Item name="end_day" label="B站爬取结束日"><Input /></Form.Item>
          <Form.Item name="all_day" label="B站按天爬取" valuePropName="checked"><Switch /></Form.Item>
          <Form.Item name="creator_mode" label="B站creator模式" valuePropName="checked"><Switch /></Form.Item>
          <Form.Item name="start_contacts_page" label="B站粉丝起始页"><Input type="number" /></Form.Item>
          <Form.Item name="crawler_max_contacts_count_singlenotes" label="B站单作者粉丝/关注数"><Input type="number" /></Form.Item>
          <Form.Item name="crawler_max_dynamics_count_singlenotes" label="B站单作者动态数"><Input type="number" /></Form.Item>
        </Collapse.Panel>
      </Collapse>
      <Form.Item>
        <Button type="primary" htmlType="submit">保存配置</Button>
        <Button type="default" onClick={() => onStart(form.getFieldsValue())} style={{marginLeft:8}}>启动爬虫</Button>
      </Form.Item>
    </Form>
  );
} 