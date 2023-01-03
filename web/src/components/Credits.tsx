import { FC } from 'react'
import A from './A'

const Credits: FC = () => (
    <div className="text-end text-xs">
        <div>
            Bachelor project @ <A href="https://ww2.mini.pw.edu.pl">MiNI</A>{' '}
            Computer Science
        </div>
        <div>by Weronika Piotrowska & Szymon Górski & Marcin Wojnarowski</div>
    </div>
)

export default Credits
