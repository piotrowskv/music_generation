import { FC } from 'react'
import Link from './Link'

const Credits: FC = () => (
    <div className="text-end text-xs">
        <div>
            Bachelor project @{' '}
            <Link href="https://ww2.mini.pw.edu.pl">MiNI</Link> Computer Science
        </div>
        <div>by Weronika Piotrowska & Szymon Górski & Marcin Wojnarowski</div>
    </div>
)

export default Credits
