import { useEffect } from 'react';
import { wechatLogin, getStudentId } from './utils/auth';
import './app.scss';

function App({ children }) {
  useEffect(() => {
    console.log('App launched.');
    
    // 启动时自动登录
    const studentId = getStudentId();
    if (!studentId) {
      wechatLogin().then((info) => {
        if (info) {
          console.log('微信登录成功:', info.student_id, info.name);
        } else {
          console.log('微信登录失败或当前非微信环境');
        }
      }).catch((err) => {
        console.error('登录异常:', err);
      });
    } else {
      console.log('已登录:', studentId);
    }
  }, []);

  return children;
}

export default App;
