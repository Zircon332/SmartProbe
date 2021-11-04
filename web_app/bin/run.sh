BINPATH=`dirname $0`

cd "${BINPATH}/.."
ROOT=$(pwd)

export FLASK_APP=smartprobe_web
export FLASK_ENV=development

flask run --host 0.0.0.0
