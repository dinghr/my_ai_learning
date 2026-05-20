import { View } from '@tarojs/components'
import './index.scss'

interface SpinosaurusProps {
  size?: number
  mood?: 'normal' | 'happy'
}

export default function Spinosaurus({ size = 130, mood = 'normal' }: SpinosaurusProps) {
  const animationClass = mood === 'happy' ? 'dino-happy' : 'dino-breathe'

  return (
    <View className='spinosaurus-wrap' style={{ width: size, height: size * 0.8 }}>
      <svg
        className={animationClass}
        viewBox='0 0 160 130'
        style={{ width: '100%', height: '100%' }}
      >
        <defs>
          <linearGradient id='bodyGrad' x1='0%' y1='0%' x2='100%' y2='100%'>
            <stop offset='0%' stopColor='#D4A052' />
            <stop offset='50%' stopColor='#B78134' />
            <stop offset='100%' stopColor='#8B6914' />
          </linearGradient>
          <linearGradient id='bodyHighlight' x1='0%' y1='0%' x2='0%' y2='100%'>
            <stop offset='0%' stopColor='#E8C880' stopOpacity='0.6' />
            <stop offset='100%' stopColor='#E8C880' stopOpacity='0' />
          </linearGradient>
          <linearGradient id='spineGrad' x1='0%' y1='0%' x2='0%' y2='100%'>
            <stop offset='0%' stopColor='#C17817' />
            <stop offset='100%' stopColor='#8B4513' />
          </linearGradient>
          <filter id='dropShadow'>
            <feDropShadow dx='2' dy='4' stdDeviation='3' floodColor='#3D2B1F' floodOpacity='0.25' />
          </filter>
        </defs>

        {/* 尾巴 */}
        <path d='M110 70 Q140 62 155 72 Q140 82 110 78 Z' fill='url(#bodyGrad)' filter='url(#dropShadow)' />
        <path d='M120 70 L125 68 M130 69 L135 67 M140 70 L145 69' stroke='#8B6914' strokeWidth='1.5' strokeLinecap='round' opacity='0.5' />

        {/* 后腿 */}
        <ellipse cx='95' cy='100' rx='10' ry='14' fill='#8B6914' filter='url(#dropShadow)' />

        {/* 身体 */}
        <ellipse cx='85' cy='75' rx='38' ry='26' fill='url(#bodyGrad)' filter='url(#dropShadow)' />
        <ellipse cx='78' cy='68' rx='25' ry='14' fill='url(#bodyHighlight)' />
        <circle cx='75' cy='72' r='2' fill='#8B6914' opacity='0.3' />
        <circle cx='85' cy='78' r='2' fill='#8B6914' opacity='0.3' />
        <circle cx='95' cy='74' r='2' fill='#8B6914' opacity='0.3' />

        {/* 背棘 */}
        <path d='M55 65 L58 38 L62 58 L66 32 L70 55 L74 28 L78 52 L82 30 L86 50 L90 35 L94 52 L98 40' fill='none' stroke='url(#spineGrad)' strokeWidth='5' strokeLinecap='round' filter='url(#dropShadow)' />
        <path d='M56 60 L59 42 L63 55' fill='none' stroke='#E8A838' strokeWidth='1.5' strokeLinecap='round' opacity='0.5' />

        {/* 头部 */}
        <ellipse cx='48' cy='62' rx='24' ry='18' fill='url(#bodyGrad)' filter='url(#dropShadow)' />
        <ellipse cx='42' cy='55' rx='14' ry='8' fill='url(#bodyHighlight)' />

        {/* 嘴巴 */}
        <path d='M28 68 Q42 74 56 68' fill='none' stroke='#8B6914' strokeWidth='2.5' strokeLinecap='round' />
        <path d='M30 66 L26 68 L30 70' fill='#8B6914' opacity='0.6' />

        {/* 眼睛 */}
        <ellipse cx='40' cy='56' rx='7' ry='6' fill='white' filter='url(#dropShadow)' />
        <ellipse cx='39' cy='56' rx='5' ry='4.5' fill='#3D2B1F' />
        <circle cx='37' cy='54' r='2.5' fill='white' />
        <circle cx='41' cy='58' r='1' fill='white' opacity='0.7' />
        <path d='M34 50 Q40 47 46 50' fill='none' stroke='#8B6914' strokeWidth='2' strokeLinecap='round' />

        {/* 鼻孔 */}
        <ellipse cx='30' cy='60' rx='2' ry='1.5' fill='#8B6914' opacity='0.6' />

        {/* 前腿 */}
        <ellipse cx='72' cy='102' rx='11' ry='16' fill='url(#bodyGrad)' filter='url(#dropShadow)' />
        <ellipse cx='68' cy='114' rx='3' ry='2' fill='#8B6914' />
        <ellipse cx='74' cy='115' rx='3' ry='2' fill='#8B6914' />
        <ellipse cx='80' cy='114' rx='3' ry='2' fill='#8B6914' />

        {/* 手臂 */}
        <ellipse cx='62' cy='78' rx='9' ry='5' fill='#8B6914' transform='rotate(-25 62 78)' filter='url(#dropShadow)' />
        <path d='M56 80 L54 83 M59 81 L58 84' stroke='#5D4E37' strokeWidth='1.5' strokeLinecap='round' />

        {/* 考古帽 */}
        <path d='M24 48 L62 48 L56 35 L30 35 Z' fill='#5D4E37' filter='url(#dropShadow)' />
        <path d='M28 40 L40 38 L48 40' fill='none' stroke='#8B7355' strokeWidth='2' strokeLinecap='round' opacity='0.5' />
        <rect x='18' y='46' width='50' height='5' rx='2.5' fill='#4A3C2A' filter='url(#dropShadow)' />
        <rect x='24' y='48' width='38' height='3' fill='#C17817' opacity='0.8' />

        {/* 背包 */}
        <rect x='88' y='72' width='14' height='16' rx='4' fill='#5D4E37' filter='url(#dropShadow)' />
        <rect x='90' y='74' width='10' height='8' rx='2' fill='#8B7355' opacity='0.5' />
        <path d='M88 74 L82 78 M102 74 L108 78' stroke='#5D4E37' strokeWidth='2' strokeLinecap='round' />

        {/* 放大镜 */}
        <circle cx='108' cy='68' r='7' fill='none' stroke='#8B7355' strokeWidth='2.5' filter='url(#dropShadow)' />
        <circle cx='108' cy='68' r='5' fill='rgba(255,255,255,0.15)' />
        <line x1='113' y1='73' x2='118' y2='80' stroke='#8B7355' strokeWidth='2.5' strokeLinecap='round' />
      </svg>
      <View className='dino-name'>小棘</View>
    </View>
  )
}
