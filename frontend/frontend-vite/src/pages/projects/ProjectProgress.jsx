import { useEffect, useState } from "react"
import api from "../../api/api"
const STATUS_PROGRESS = {
    "Not Started": 0,
    "Planned":     10,
    "In Progress": 50,
    "Completed":   100,
    "On Hold":     25,
}
const STATUS_COLOR = {
    "Not Started": "bg-gray-400",
    "Planned":     "bg-blue-400",
    "In Progress": "bg-yellow-400",
    "Completed":   "bg-green-500",
    "On Hold":     "bg-red-400",
}
export default function ProjectProgress() {
    const [projects, setProjects] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")
    useEffect(() => {
        loadProjects()
    }, [])
    const loadProjects = async () => {
        try {
            const res = await api.get("/api/projects")
            // API returns { data: [...], success: true, message: "..." }
            const projectsData = Array.isArray(res.data?.data)
                ? res.data.data
                : Array.isArray(res.data)
                ? res.data
                : []
            setProjects(projectsData)
        } catch (err) {
            setError(err.response?.data?.error || "Failed to load projects")
            setProjects([]) // Ensure projects is always an array
        } finally {
            setLoading(false)
        }
    }
    return (
        <div className="theme-blue-white" style={{ background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)', minHeight: '100vh', padding: '24px' }}>
            <h1 className="text-2xl font-bold mb-6" style={{ color: '#0052CC' }}>Project Progress</h1>
            {error && <div className="text-red-600 mb-4">{error}</div>}
            <div className="card-blue-white" style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)' }}>
                {loading ? (
                    <p className="text-gray-500">Loading...</p>
                ) : projects.length === 0 ? (
                    <p className="text-gray-500">No projects found.</p>
                ) : projects.map(p => {
                    const progress = STATUS_PROGRESS[p.status] ?? 0
                    const color = STATUS_COLOR[p.status] ?? "bg-gray-400"
                    return (
                        <div key={p.id}>
                            <div className="flex justify-between mb-1">
                                <span className="font-medium">{p.name}</span>
                                <span className="text-sm text-gray-500">{p.status} — {progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 h-3 rounded">
                                <div
                                    className={`${color} h-3 rounded transition-all`}
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
