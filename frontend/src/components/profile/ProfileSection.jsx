import { useState } from 'react'
import { BlurFade } from '../magicui/blur-fade'
import confetti from 'canvas-confetti'

const OCCUPATIONS = ['salaried', 'self-employed', 'business-owner', 'retired', 'student']
const GENDERS = ['male', 'female', 'prefer-not-to-say']

export default function ProfileSection({ userProfile = {}, onProfileSave }) {
  const [form, setForm] = useState({
    name: '', age: '', annualIncome: '', smoker: false,
    gender: '', occupation: 'salaried', dependents: 0,
    ...userProfile,
  })
  const [saved, setSaved] = useState(false)

  const update = (key, value) => setForm(prev => ({ ...prev, [key]: value }))

  const handleSave = () => {
    onProfileSave?.(form)
    setSaved(true)
    confetti({ particleCount: 80, spread: 60, origin: { y: 0.6 }, colors: ['#fff', '#888', '#444'] })
    setTimeout(() => setSaved(false), 3000)
  }

  const inputClass = "w-full bg-[#0f0f0f] border border-[#1e1e1e] rounded-lg px-3 py-2 text-[13px] text-[#e4e4e7] placeholder-[#333] focus:outline-none focus:border-[#333] transition-colors"
  const labelClass = "block text-[11px] font-medium text-[#555] uppercase tracking-wider mb-1.5"

  return (
    <div className="h-full overflow-y-auto px-6 py-6
      [&::-webkit-scrollbar]:w-[3px]
      [&::-webkit-scrollbar-track]:bg-transparent
      [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
    >
      <div className="max-w-xl mx-auto">
        <BlurFade delay={0.05}>
          <h2 className="text-[15px] font-semibold text-[#e4e4e7] mb-1">Your Insurance Profile</h2>
          <p className="text-[12px] text-[#444] mb-6">This profile helps the AI advisor tailor recommendations to your specific situation.</p>
        </BlurFade>

        <div className="flex flex-col gap-5">
          {/* Name */}
          <BlurFade delay={0.1}>
            <label className={labelClass}>Full Name</label>
            <input className={inputClass} value={form.name} onChange={e => update('name', e.target.value)} placeholder="Your name" />
          </BlurFade>

          {/* Age + Income */}
          <BlurFade delay={0.15}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Age</label>
                <input type="number" className={inputClass} value={form.age} onChange={e => update('age', e.target.value)} placeholder="e.g. 32" min={18} max={70} />
              </div>
              <div>
                <label className={labelClass}>Annual Income (₹)</label>
                <input type="number" className={inputClass} value={form.annualIncome} onChange={e => update('annualIncome', e.target.value)} placeholder="e.g. 1800000" />
              </div>
            </div>
          </BlurFade>

          {/* Gender + Occupation */}
          <BlurFade delay={0.2}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Gender</label>
                <select className={inputClass} value={form.gender} onChange={e => update('gender', e.target.value)}>
                  <option value="">Select</option>
                  {GENDERS.map(g => <option key={g} value={g}>{g.replace('-', ' ')}</option>)}
                </select>
              </div>
              <div>
                <label className={labelClass}>Occupation</label>
                <select className={inputClass} value={form.occupation} onChange={e => update('occupation', e.target.value)}>
                  {OCCUPATIONS.map(o => <option key={o} value={o}>{o.replace('-', ' ')}</option>)}
                </select>
              </div>
            </div>
          </BlurFade>

          {/* Dependents */}
          <BlurFade delay={0.25}>
            <label className={labelClass}>Number of Dependents</label>
            <input type="number" className={inputClass} value={form.dependents} onChange={e => update('dependents', parseInt(e.target.value) || 0)} min={0} max={10} />
          </BlurFade>

          {/* Smoker toggle */}
          <BlurFade delay={0.3}>
            <div className="flex items-center justify-between p-4 bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg">
              <div>
                <p className="text-[13px] text-[#e4e4e7] font-medium">Smoker</p>
                <p className="text-[11px] text-[#444] mt-0.5">Smokers pay ~30% higher premiums</p>
              </div>
              <button
                onClick={() => update('smoker', !form.smoker)}
                className={`relative w-10 h-5 rounded-full transition-colors ${form.smoker ? 'bg-white' : 'bg-[#222]'}`}
              >
                <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-[#0f0f0f] transition-transform ${form.smoker ? 'translate-x-5' : ''}`} />
              </button>
            </div>
          </BlurFade>

          {/* Save button */}
          <BlurFade delay={0.35}>
            <button
              onClick={handleSave}
              className="w-full py-2.5 bg-white text-black text-[13px] font-medium rounded-lg hover:bg-[#e4e4e7] transition-colors active:scale-[0.99]"
            >
              {saved ? '✓ Profile Saved!' : 'Save Profile'}
            </button>
          </BlurFade>
        </div>
      </div>
    </div>
  )
}
