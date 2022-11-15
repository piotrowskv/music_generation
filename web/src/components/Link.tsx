import React, { ReactNode } from 'react'

interface Props {
    href: string
    children: ReactNode
}

const Link: React.FC<Props> = ({ href, children }) => (
    <a
        href={href}
        className="text-sky-600 transition-colors hover:text-sky-400"
    >
        {children}
    </a>
)

export default Link
