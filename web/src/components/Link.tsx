import React, { ReactNode } from 'react'

interface Props {
    href: string
    children: ReactNode
}

const Link: React.FC<Props> = ({ href, children }) => (
    <a href={href} className="duration-250 text-sky-600 hover:text-sky-400">
        {children}
    </a>
)

export default Link
