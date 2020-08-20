import { all, call, put, take, takeEvery } from "redux-saga/effects";
import uuid from 'uuid/v4';
import * as channelActions from '../channel/actions';
import { ClusterDetailsResponse, ConnectResponse } from "../messages";
import * as clusterActions from './actions';
import { checkClusterConnection, connectToCluster, getClusterDetail } from "./api";

function* connectSaga(action: ReturnType<typeof clusterActions.Actions.connect>) {
    yield put(clusterActions.Actions.connecting())
    const conn: ConnectResponse = yield call(connectToCluster, action.payload.params);
    yield call(putClusterStatus, conn);
}

function* putClusterStatus(conn: ConnectResponse) {
    if (conn.status === "ok") {
        const clusterDetails:ClusterDetailsResponse = yield call(getClusterDetail)
        yield put(clusterActions.Actions.connected(conn.connection.connection, clusterDetails.details));
    } else if (conn.status === "error") {
        yield put(clusterActions.Actions.notConnected());
        const timestamp = Date.now();
        const id = uuid();
        yield put(clusterActions.Actions.error(`error connecting to cluster: ${conn.msg}`,timestamp, id));
    } else {
        yield put(clusterActions.Actions.notConnected());
    }
}

/**
 * when the channel is connected, check if cluster is connected and update status accordingly
 */
function* trackClusterConnection() {
    while (true) {
        yield take(channelActions.ActionTypes.OPEN)
        const conn: ConnectResponse = yield call(checkClusterConnection);
        yield call(putClusterStatus, conn);
    }
}

export function* clusterConnectionSaga() {
    yield takeEvery(clusterActions.ActionTypes.CONNECT, connectSaga);
    yield all([
        trackClusterConnection(),
    ])
}