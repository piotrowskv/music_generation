import React from 'react'

interface Props extends React.HTMLAttributes<HTMLOrSVGElement> {}

const MusicNote: React.FC<Props> = props => (
    <svg {...props}>
        <path d="M16.75 32.417q-1.833 0-3.125-1.292T12.333 28q0-1.833 1.292-3.125t3.125-1.292q.958 0 1.875.396t1.542 1.146V7.583h7.5v3.292h-6.5V28q0 1.833-1.292 3.125t-3.125 1.292Z" />
    </svg>
)

export default MusicNote
